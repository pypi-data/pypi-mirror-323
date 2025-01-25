"""
DAG de Airflow para la ingestión y procesamiento de datos desde Oracle a BigQuery utilizando Dataflow.

Este DAG realiza las siguientes tareas:
1. Ejecuta un job de Dataflow (ingestión) que extrae datos desde una base de datos Oracle y los almacena en GCS en formato Avro.
2. Copia el archivo Avro generado desde la capa de ingest a la capa raw en GCS.
3. Ejecuta un job de Dataflow (depuración) que carga los datos desde el archivo Avro en GCS a una tabla de BigQuery.

El DAG está parametrizado para facilitar su configuración en diferentes entornos (dev, qa, prd) y para diferentes tablas.
"""

from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.providers.google.cloud.operators.dataflow import DataflowStartFlexTemplateOperator
from airflow.providers.google.cloud.transfers.gcs_to_gcs import GCSToGCSOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.providers.google.cloud.operators.bigquery import BigQueryInsertJobOperator
from airflow.utils.task_group import TaskGroup
from utils.notifications import google_chat_notification
from utils.load_sql_from_gcs import load_sql_query_from_gcs
from utils.dataflow_body import create_dataflow_body
from utils.df_job_name import ajust_job_name
from utils.success_log import success_log
from utils.load_tables import download_file_from_gcs, load_tables_to_process
from airflow.models import Variable
from datetime import datetime

# Definición de IDs de secretos necesarios para la conexión a la base de datos (si aplica)
SECRET_IDS = {
    'host': '',      # ID del secreto que contiene el host de la base de datos
    'user': '',      # ID del secreto que contiene el usuario de la base de datos
    'password': '',  # ID del secreto que contiene la contraseña de la base de datos
    'sid': ''        # ID del secreto que contiene el SID de la base de datos
}

# Obtención de variables de Airflow para configuración del DAG y de los jobs de Dataflow
CONFIG_VARS = {
    'output_bucket_ingest': Variable.get('OUTPUT_BUCKET_INGEST'),                 # Bucket de salida para la capa de ingest
    'output_bucket_raw': Variable.get('OUTPUT_BUCKET_RAW'),                       # Bucket de salida para la capa raw
    'base_path_dataflow_templates': Variable.get('TEMPLATES_PATH'),               # Ruta base donde se encuentran los templates de Dataflow
    'dataflow_workspace_bucket': Variable.get('BUCKET_DF_BATCH'),                 # Bucket de trabajo para Dataflow
    'data_ingest_service_account': Variable.get('SERVICE_ACCOUNT_DATA_INGEST'),   # Service Account utilizada para los jobs de Dataflow
    'subnetwork': Variable.get('SUBNETWORK'),                                     # Subred utilizada por Dataflow
    'network': Variable.get('NETWORK'),                                           # Red utilizada por Dataflow
    'data_ingest_project_id': Variable.get('DATA_INGEST_PROJECT_ID'),             # ID del proyecto donde se ejecuta la ingestión de datos
    'datagov_project_id': Variable.get('DATAGOV_PROJECT_ID'),                     # ID del proyecto Data Governance
    'location': Variable.get('LOCATION'),                                         # Ubicación (región) donde se ejecutan los jobs
    'lakehouse_andes_analitico_project_id': Variable.get('PROJECT_LAKEHOUSE_ID'),           # ID del proyecto Lakehouse Andes
    'lakehouse_andes_ops_project_id': Variable.get('LAKEHOUSE_ANDES_OPS_PROJECT_ID'),
    'env': Variable.get('ENV'),                                                   # Entorno (dev, qa, prd)
    'bucket_schemas_avro': f"schemas_avro_{Variable.get('ENV')}"                        # Bucket donde se almacenan los esquemas Avro
}

# --- Configuración de rutas y constantes específicas ---

# Nombre del DAG (debe ser el mismo nombre del archivo .py)
DAG_NAME = ""  # Reemplazar con el nombre del archivo .py (sin la extensión)

# Fecha de procesamiento (en formato YYYYMMDD)
PROCESS_DATE = datetime.now().strftime('%Y%m%d')

# Programación del DAG (vacío en producción para ejecutar inmediatamente, None en otros entornos para no programar)
SCHEDULE = '' if CONFIG_VARS['env'] == 'prd' else None

# Bucket donde se encuentran las consultas SQL para Oracle
BUCKET_QUERY = f"querys-oracle-{CONFIG_VARS['env']}"

# Configuración de rutas y buckets
GCS_BUCKET_NAME = f"resources_config_dag_{CONFIG_VARS['env']}"
GCS_OBJECT_NAME = "path/to/tables_to_process.py"  # Ruta del archivo en el bucket
LOCAL_FILE_PATH = "/tmp/tables_to_process.py"  # Ruta temporal en el sistema local

# Cargar la variable TABLES_TO_PROCESS
download_file_from_gcs(GCS_BUCKET_NAME, GCS_OBJECT_NAME, LOCAL_FILE_PATH)
TABLES_TO_PROCESS = load_tables_to_process(LOCAL_FILE_PATH)

# Argumentos por defecto para el DAG
DEFAULT_ARGS = {
    'start_date': days_ago(1),
    'email_on_failure': False,
    'email_on_retry': False,
    "retries": 0,
}


# Definición del DAG de Airflow
with DAG(
    DAG_NAME,                         # Nombre del DAG
    default_args=DEFAULT_ARGS,        # Argumentos por defecto
    schedule_interval=SCHEDULE,       # Programación del DAG
    catchup=False,                    # No ejecutar tareas atrasadas
    tags=[CONFIG_VARS['env']]         # Etiquetas (tags) del DAG (por ejemplo, el entorno)
) as dag:

    # Tarea inicial (DummyOperator)
    start = DummyOperator(
        task_id='start'
    )

    # Tarea final (DummyOperator)
    end = DummyOperator(
        task_id='end'
    )

    # Tarea de ingestión (ejecuta el job de Dataflow para extraer datos de Oracle a GCS en formato Avro)
    groups = []

    for table in TABLES_TO_PROCESS:
        with TaskGroup(group_id=f"oracle_to_bq_{table['oracle_table'].lower()}") as group:
            entorno = table['entorno']
            # Definicion de proyecto de bigquery
            if entorno == 'analitico':
                bigquery_project_id = CONFIG_VARS['lakehouse_andes_analitico_project_id']
                staging_dataset = "staging_dataset"
            elif entorno == 'operacional':
                bigquery_project_id = CONFIG_VARS['lakehouse_andes_ops_project_id']
                staging_dataset = "staging"

            table_name = table['oracle_table'].lower()
            origen = table['origen']
            dominio = table['dominio']
            producto = table['producto']
            subdominio = table['subdominio']
            raw_file_path = f"{table['gcs_raw_path']}/{PROCESS_DATE}/{table['oracle_table']}.avro"
            raw_destination_path = f"{table['gcs_raw_path']}/{PROCESS_DATE}/"
            tabla_staging = f"{bigquery_project_id}.{staging_dataset}.stg_{table_name}"
            tabla_destino = f"{bigquery_project_id}.{table['dataset_destino']}.dep_{table_name}"

            # Ruta y nombre del archivo SQL dentro del bucket (reemplazar con tu ruta)
            object_query_name = f"{dominio}/{subdominio}/{producto}/{origen}/{entorno}/{table_name}.sql"
            query = load_sql_query_from_gcs(BUCKET_QUERY, object_query_name)
            
            with TaskGroup(group_id=f"oracle_raw_ingestion_{table['oracle_table'].lower()}") as oracle_raw_ingestion:

                # Agrupacion de tareas
                ingest = DataflowStartFlexTemplateOperator(
                    task_id=f"ingest_{table_name}",
                    body=create_dataflow_body(
                            # Nombre del job de Dataflow (reemplazar <origen>, <dominio>, <subdominio>, <tabla>)
                            job_name= ajust_job_name(f"df-batch-{origen}-ingest-{dominio}-{subdominio}-{table_name}"),

                            # Ruta al archivo JSON del template de Dataflow (Jdbc-To-Gcs-Avro)
                            container_spec_path=f"{CONFIG_VARS['base_path_dataflow_templates']}/Jdbc-To-Gcs-Avro/Jdbc-To-Gcs-Avro.json",

                            # Parámetros para el job de Dataflow
                            parameters={
                                'secret_id_host': SECRET_IDS['host'],  # ID del secreto del host de la base de datos
                                'port': '1521',                        # Puerto de la base de datos Oracle
                                'secret_id_service_name': SECRET_IDS['sid'],  # ID del secreto del SID (Service Name) de la base de datos
                                'secret_id_user': SECRET_IDS['user'],  # ID del secreto del usuario de la base de datos
                                'secret_id_password': SECRET_IDS['password'],  # ID del secreto de la contraseña de la base de datos
                                'datagov_project_id': CONFIG_VARS['datagov_project_id'],  # ID del proyecto de Data Governance
                                'query': query,                        # Consulta SQL a ejecutar en Oracle
                                'table_name': table['oracle_table'],       # Nombre de la tabla en Oracle
                                'avro_schema_gcs_path': f"gs://{CONFIG_VARS['bucket_schemas_avro']}/{table['gcs_schema_avsc_path']}/{table_name}.avsc",  # Ruta al esquema Avro en GCS
                                'output_path': f"gs://{CONFIG_VARS['output_bucket_ingest']}/{table['gcs_ingest_path']}",        # Ruta de salida en GCS para el archivo Avro
                                'output_prefix': table['oracle_table'],    # Prefijo para el archivo de salida
                                'data_type_schema_gcs_path': f"gs://data_type_mappings_{CONFIG_VARS['env']}/{table['gcs_schema_json_path']}/{table_name}.json",  # Ruta al mapeo de tipos de datos
                            }
                        ),
                    location=CONFIG_VARS['location'],
                    project_id=CONFIG_VARS['data_ingest_project_id'],
                    on_failure_callback=google_chat_notification  # Notificación en caso de falla
                )

                raw = GCSToGCSOperator(
                    task_id=f"raw_{table_name}",
                    source_bucket=CONFIG_VARS['output_bucket_ingest'],  # Bucket de origen (capa ingest)
                    source_object=f"{table['gcs_ingest_path']}/{table['oracle_table']}.avro",  # Objeto (archivo Avro) de origen
                    destination_bucket=CONFIG_VARS['output_bucket_raw'],  # Bucket de destino (capa raw)
                    destination_object=raw_destination_path,  # Objeto (ruta) de destino
                    move_object=False,  # No mover el objeto, solo copiarlo
                    on_failure_callback=google_chat_notification  # Notificación en caso de falla
                )

                ingest >> raw
            
            with TaskGroup(group_id=f"load_and_depure_to_bq_{table['oracle_table'].lower()}") as load_and_depure_to_bq:

                if table["load_mode"] == "full":
                    truncate_table = BigQueryInsertJobOperator(
                        task_id='truncate_table',
                        configuration={
                            "query": {
                                "query": f"""
                                    DELETE FROM `{bigquery_project_id}.{table["dataset_destino"]}.dep_{table["bigquery_table"]}`
                                    WHERE TRUE
                                    """,
                                "useLegacySql": False,  # Siempre usar SQL estándar
                            }
                        },
                        location= CONFIG_VARS['location'],  # Cambia a la región de tu BigQuery si es necesario
                        on_failure_callback=google_chat_notification  # Notificación en caso de falla
                    )
                
                insert_to_bq = BigQueryInsertJobOperator(
                    task_id=f'avro_to_bq_{table_name}',
                    configuration={
                        "load": {
                            "sourceUris": [f"gs://{CONFIG_VARS['output_bucket_raw']}/{raw_file_path}"],
                            "destinationTable": {
                                "projectId": bigquery_project_id,
                                "datasetId": staging_dataset,
                                "tableId": f"stg_{table_name}",
                            },
                            "sourceFormat": "AVRO",
                            "writeDisposition": "WRITE_TRUNCATE"
                        }
                    },
                    location=CONFIG_VARS['location'],
                    on_failure_callback=google_chat_notification  # Notificación en caso de falla
                )

                
                # Tarea para realizar el upsert en caso de aplicar 
                merge_table = BigQueryInsertJobOperator(
                    task_id=f"merge_table_{table_name}",  # ID de la tarea, dinámicamente generado
                    configuration={
                        "query": {
                            "query": f"CALL `{bigquery_project_id}.{table['dataset_destino']}.{table['store_procedure']}`()",  # Llamada al procedimiento almacenado
                            "useLegacySql": False,  # Usar SQL estándar en lugar de Legacy SQL
                            "priority": "BATCH",  # Prioridad del trabajo en BigQuery
                        }
                    },
                    location=CONFIG_VARS['location'],  # Ubicación geográfica de BigQuery
                    on_failure_callback=google_chat_notification,  # Callback en caso de fallo de la tarea
                    on_success_callback=success_log # Callback en caso de exito de la tarea
                )

                if table['load_mode'] == "full":
                    truncate_table >> insert_to_bq >> merge_table
                else:
                    insert_to_bq >> merge_table



            audit_merge = BigQueryInsertJobOperator(
                task_id=f"audit_merge_{table_name}",  # ID de la tarea, dinámicamente generado
                configuration={
                    "query": {
                        "query": f"""
                            CALL `{bigquery_project_id}.monitoreo.sp_calcular_auditoria`(
                                '{{{{ task_instance.xcom_pull(task_ids="oracle_to_bq_{table_name}.load_and_depure_to_bq_{table_name}.merge_table_{table_name}", key="return_value") }}}}',
                                '{table_name}', 
                                '{tabla_destino}',
                                '{tabla_staging}'
                            )
                        """,  # Llamada al procedimiento almacenado
                        "useLegacySql": False,  # Usar SQL estándar en lugar de Legacy SQL
                        "priority": "BATCH",  # Prioridad del trabajo en BigQuery
                    }
                },
                location=CONFIG_VARS['location'],  # Ubicación geográfica de BigQuery
                on_failure_callback=google_chat_notification  # Callback en caso de fallo de la tarea
            )


            start >> oracle_raw_ingestion  >> load_and_depure_to_bq >> audit_merge >> end

            

    groups.append(group)
    
   

    
    
     



        
 
