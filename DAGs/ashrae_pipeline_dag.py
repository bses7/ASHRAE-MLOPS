from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
from airflow.models import Variable

PROJECT_HOME = Variable.get("PROJECT_HOME")
VENV = Variable.get("VENV")
CONFIG_PATH = Variable.get("CONFIG_PATH")
VENV_PATH = Variable.get("VENV_PATH")

default_args = {
    'owner': 'bishesh',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG(
    'ashrae_pipeline_dag',
    default_args=default_args,
    description='ASHRAE Great Energy Predictor III MLOPS Opeation',
    schedule_interval=None,
    start_date=datetime(2023, 1, 1),
    catchup=False,
    tags=['mlops', 'ingestion', 'ashrae'],
) as dag:

    ingest_data = BashOperator(
        task_id='ingest_raw_data_to_mariadb',
        bash_command=f"""
            cd {PROJECT_HOME} &&
            {VENV_PATH} \
            main.py --stage ingestion --config {CONFIG_PATH}
        """
    )

    preprocess_data = BashOperator(
        task_id='preprocess_data',
        bash_command=f"""
            cd {PROJECT_HOME} &&
            {VENV_PATH} \
            main.py --stage preprocessing --config {CONFIG_PATH}
        """
    )

    train_model = BashOperator(
        task_id='train_model',
        bash_command=f"""
            cd {PROJECT_HOME} &&
            {VENV_PATH}  \
            main.py --stage train --config {CONFIG_PATH}
        """
    )

    ingest_data >> preprocess_data >> train_model
