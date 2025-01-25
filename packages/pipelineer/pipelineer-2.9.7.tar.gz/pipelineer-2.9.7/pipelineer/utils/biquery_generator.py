import os
import json

class BigQueryScriptGenerator:
    """
    Clase para generar procedimientos almacenados y scripts de creación de tablas en BigQuery.
    """
    def __init__(self, template_folder, schema_folder, output_folder):
        self.template_folder = template_folder
        self.schema_folder = schema_folder
        self.output_folder = output_folder

    def generate_bigquery_store_procedures(self):
        """
        Genera procedimientos almacenados para MERGE en BigQuery basado en tablas configuradas en `resources_config.py`.
        """
        resources_config_path = os.path.join(self.template_folder, "resources_config.py")

        if not os.path.exists(resources_config_path):
            raise FileNotFoundError(f"El archivo 'resources_config.py' no existe en {self.template_folder}")

        if not os.path.isdir(self.schema_folder):
            raise ValueError(f"La carpeta de esquemas no existe: {self.schema_folder}")

        if not os.path.isdir(self.output_folder):
            os.makedirs(self.output_folder)

        # Cargar configuración desde resources_config.py
        resources_config = {}
        with open(resources_config_path, "r") as file:
            exec(file.read(), resources_config)

        resources = resources_config.get("RESOURCES_CONFIG", {})
        if not resources:
            raise ValueError("El archivo resources_config.py no contiene la clave 'RESOURCES_CONFIG'.")

        dataset_destino = resources["dataset_destino"]
        tablas = resources["tablas"]

        for tabla in tablas:
            table_name = tabla["nombre"]
            schema_file = os.path.join(self.schema_folder, f"{table_name.lower()}.sql")

            if not os.path.isfile(schema_file):
                print(f"Esquema no encontrado: {schema_file}. Saltando {table_name}.")
                continue

            fields, primary_keys = self.parse_oracle_schema(schema_file)

            if not fields or not primary_keys:
                print(f"No se encontraron campos o claves primarias en el esquema de {table_name}. Saltando.")
                continue

            date_fields = [field[0] for field in fields if field[1] in ("DATETIME", "DATE")]

            all_fields = [field[0] for field in fields]
            all_fields.append("fecha_creacion")
            all_fields.append("fecha_actualizacion")

            target_table = f"${{PROJECT_NAME}}.{dataset_destino}.dep_{table_name.lower()}"
            source_table = f"${{PROJECT_NAME}}.staging_dataset.stg_{table_name.lower()}"
            procedure_name = f"{dataset_destino}.sp_merge_dep_{table_name.lower()}"

            on_clause = " AND ".join([f"T.{pk} = S.{pk}" for pk in primary_keys])

            update_fields = [
                f"T.{field} = " + (f"CAST(S.{field} AS DATETIME)" if field in date_fields else f"S.{field}")
                for field in all_fields if field not in ["fecha_creacion", "fecha_actualizacion"]
            ]
            update_clause = ",\n      ".join(update_fields)
            update_clause += ",\n      T.fecha_actualizacion = DATETIME_TRUNC(CURRENT_DATETIME('America/Santiago'), SECOND)"

            insert_fields = ",\n      ".join([field for field in all_fields if field != "fecha_actualizacion"])
            insert_values = ",\n      ".join([
                f"CAST(S.{field} AS DATETIME)" if field in date_fields else (
                    "DATETIME_TRUNC(CURRENT_DATETIME('America/Santiago'), SECOND)" if field == "fecha_creacion" else f"S.{field}"
                )
                for field in all_fields if field != "fecha_actualizacion"
            ])

            procedure_script = f"""
CREATE OR REPLACE PROCEDURE `${{PROJECT_NAME}}.{procedure_name}`()
BEGIN
  MERGE `{target_table}` T
  USING `{source_table}` S
  ON {on_clause}
  WHEN MATCHED THEN
    UPDATE SET
      {update_clause}
  WHEN NOT MATCHED THEN
    INSERT (
      {insert_fields}
    )
    VALUES (
      {insert_values}
    );
END;
"""
            output_file = os.path.join(self.output_folder, f"sp_merge_dep_{table_name.lower()}.sql")
            with open(output_file, 'w') as output:
                output.write(procedure_script)

            print(f"Procedimiento almacenado generado: {output_file}")

    def generate_bigquery_table_scripts(self, config_folder, config_file=None):
        """
        Genera scripts de creación de tablas en BigQuery con base en un archivo de configuración y esquemas Oracle.
        """
        if not os.path.isdir(config_folder):
            raise ValueError(f"La carpeta de configuración no existe: {config_folder}")
        if not os.path.isdir(self.schema_folder):
            raise ValueError(f"La carpeta de esquemas no existe: {self.schema_folder}")

        config_files = [os.path.join(config_folder, f) for f in os.listdir(config_folder) if f.endswith(".json")]
        if config_file:
            config_files = [config_file]

        if not config_files:
            raise ValueError("No se encontraron archivos de configuración en la carpeta especificada.")

        if not os.path.isdir(self.output_folder):
            os.makedirs(self.output_folder)

        for file in config_files:
            with open(file, 'r') as f:
                config = json.load(f)

            table_name = config.get("table_name")
            zones = ["stg", "dep"]
            partition_field = config.get("partition_field")
            clustering_fields = config.get("clustering_fields", [])
            partition_type = config.get("partition_type", "DAY")
            dataset = config.get("dataset")
            labels = config.get("labels", [])

            if not table_name or not dataset:
                raise ValueError(f"El archivo de configuración {file} debe contener 'table_name' y 'dataset'.")

            schema_file = os.path.join(self.schema_folder, f"{table_name.lower()}.sql")
            if not os.path.isfile(schema_file):
                print(f"Esquema no encontrado: {schema_file}. Saltando {table_name}.")
                continue

            fields, primary_keys, descriptions = self.parse_oracle_schema(schema_file)

            for zone in zones:
                zone_dataset = "staging_dataset" if zone == "stg" else dataset
                bq_table_name = f"{zone}_{table_name.lower()}"

                script_lines = [f"DROP TABLE IF EXISTS `${{PROJECT_NAME}}.{zone_dataset}.{bq_table_name}`;"]
                script_lines.append(f"CREATE TABLE IF NOT EXISTS `${{PROJECT_NAME}}.{zone_dataset}.{bq_table_name}` (")

                for column_name, column_type, is_not_null in fields:
                    null_status = "NOT NULL" if is_not_null else ""
                    script_lines.append(f"  {column_name} {column_type} {null_status},")

                script_lines.append("  fecha_creacion DATETIME DEFAULT NULL,")
                script_lines.append("  fecha_actualizacion DATETIME DEFAULT NULL")

                if script_lines[-1].endswith(","):
                    script_lines[-1] = script_lines[-1][:-1]

                if zone == "dep":
                    script_lines.append(")")
                else:
                    script_lines.append(");")

                if partition_field and zone == "dep":
                    script_lines.append(f"PARTITION BY DATETIME_TRUNC({partition_field}, {partition_type})")

                if clustering_fields and zone == "dep":
                    script_lines.append(f"CLUSTER BY {', '.join([field.lower() for field in clustering_fields])}")

                if labels and zone == "dep":
                    label_list = ", ".join([f"('{label['key']}', '{label['value']}')" for label in labels])
                    script_lines.append(f"OPTIONS(labels=[{label_list}]);")

                if primary_keys and zone == "dep":
                    pk_fields = ", ".join(primary_keys)
                    script_lines.append(f"ALTER TABLE `${{PROJECT_NAME}}.{zone_dataset}.{bq_table_name}` ADD PRIMARY KEY ({pk_fields}) NOT ENFORCED;")

                script = "\n".join(script_lines)
                output_file = os.path.join(self.output_folder, f"{zone}_{table_name.lower()}.sql")
                with open(output_file, 'w') as output:
                    output.write(script)

                print(f"Script generado: {output_file}")

    @staticmethod
    def parse_oracle_schema(schema_file):
        """
        Simula la función de parseo del esquema de Oracle. Debería ser implementada.
        """
        # Este método debe implementarse adecuadamente
        raise NotImplementedError("La función parse_oracle_schema debe ser implementada.")
