import pandas as pd
from sqlalchemy import create_engine
import psycopg2
import json
import os

def connection(username, password, host, port, database):
    connection_url = f'postgresql://{username}:{password}@{host}:{port}/{database}'
    engine = create_engine(connection_url)
    return engine

def extract_load_csv():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))

    # using dict as representative to data source path mapping [table_name --> csv location]
    csv_table = {
        'employee': os.path.join(base_dir, 'asset/csv/employee.csv'),
        'performance_rating': os.path.join(base_dir, 'asset/csv/performance_rating.csv')
    }

    with open ('dags/common_package/credentials.json', "r") as cred:
        credential_source = json.load(cred)['postgres_oltp']
    
    schema_source = 'public'
    source_engine = connection(
        credential_source['username'], 
        credential_source['password'], 
        credential_source['host'], 
        credential_source['port'],
        credential_source['database'])

    for table_name, csv_location in csv_table.items():
        if not os.path.exists(csv_location):
            raise FileNotFoundError(f"CSV file not found: {csv_location}")

        df = pd.read_csv(csv_location)
        df.to_sql(table_name, source_engine, schema = schema_source, if_exists='replace', index=False)
        

def extract_load_db():
    # [table_source -> table_name in DWH], we use {model}_{database source}_{table name source}, stg =  staging (data lake)
    mapping_table = {
        'employee':'stg_dev_employee',
        'performance_rating':'stg_dev_performance_rating'
    }

    with open ('dags/common_package/credentials.json', "r") as cred:
        credential = json.load(cred)
        credential_source = credential['postgres_oltp']
        credential_target = credential['postgres_dwh']

    schema_source = 'public'
    schema_target = 'staging' # data lake to dump data

    source_engine = connection(
        credential_source['username'], 
        credential_source['password'], 
        credential_source['host'], 
        credential_source['port'],
        credential_source['database'])
    
    target_engine = connection(
        credential_target['username'], 
        credential_target['password'], 
        credential_target['host'], 
        credential_target['port'],
        credential_target['database'])

    for table_source, table_target in mapping_table.items():
        query = f'select * from {schema_source}.{table_source}' # in ELT, table loading is 1:1 with source, read only
        source_df = pd.read_sql(query, source_engine)
        source_df.to_sql(table_target,target_engine, schema = schema_target, if_exists='replace', index=False)