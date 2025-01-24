from datetime import datetime, timedelta

from airflow import DAG
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash_operator import BashOperator
from common_package import extract_load

default_args = {
    'owner': 'alrafikri',
    'depends_on_past': False,
    'start_date': datetime(2023, 5, 1),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    dag_id="postgres_elt_dag",
    default_args=default_args,
    catchup=False,
    schedule_interval=timedelta(days=1),
) as dag:
    extract_load_csv_to_table_source = PythonOperator(
        task_id="extract_load_csv_to_table_source",
        python_callable=extract_load.extract_load_csv
    )
    
    extract_load_db_source_to_dwh = PythonOperator(
        task_id="extract_load_db_source_to_dwh",
        python_callable=extract_load.extract_load_db
    )

    run_dbt_model = BashOperator(
        task_id='run_dbt_model',
        bash_command='cd /opt/airflow/dbt/dbt_postgre && dbt run',
        dag=dag
    )

    extract_load_csv_to_table_source >> extract_load_db_source_to_dwh >> run_dbt_model