# ELT HR Analytics Project

This project performs an **ELT** (Extract, Load, Transform) process on HR analytics data, transforming raw CSV files into a Data Warehouse using Apache Airflow and DBT.

## Table of Contents

1. [Data Source](#data-source)
2. [Airflow DAGs](#airflow-dags)
3. [DBT Setup](#dbt-setup)
4. [Folder Structure](#folder-structure)
5. [Running the Project](#running-the-project)
6. [Docker Setup](#docker-setup)
7. [Contribution Guidelines](#contribution-guidelines)
8. [License](#license)
9. [Acknowledgements](#acknowledgements)

## Data Source

The data source for this project is available on Kaggle: [HR Analytics Dataset](https://www.kaggle.com/datasets/davidafolayan/hr-analytics?select=PerformanceRating.csv). The CSV files `employee.csv` and `performance_rating.csv` are used in this project.

## Setup

Follow these steps to set up and run the project:

### 1. Set Up Apache Airflow

To set up Apache Airflow, follow the official instructions for setting up Airflow with Docker Compose. You can find the full guide here:  
[Apache Airflow Docker Compose Setup](https://airflow.apache.org/docs/apache-airflow/stable/howto/docker-compose/index.html).

### 2. Start Airflow with Docker Compose

Once you have the Docker Compose configuration ready, run the following command to start Airflow in detached mode:

```
docker-compose up -d
```

This will download the required images, set up the containers, and start Airflow services in the background.

### 3. Access Airflow UI

Once the containers are up, navigate to [http://localhost:8080](http://localhost:8080) in your browser to access the Airflow web UI. You will be prompted to log in with the credentials specified in the `docker-compose.yml` file.

### 4. Set Up Connection to PostgreSQL in Airflow

To enable Airflow to connect to your PostgreSQL database, follow these steps:

1. Go to the Airflow UI and click on the "Admin" tab in the top menu.
2. Select "Connections" from the dropdown.
3. Click the "Add a new record" button.
4. In the "Conn ID" field, enter a name for the connection (e.g., `postgres_conn`).
5. In the "Conn Type" dropdown, select `Postgres`.
6. Fill in the required connection details (host, schema, login, password, port, etc.).
7. Click "Save" to save the connection settings.

### 5. Unpause the DAG

In the Airflow UI, navigate to the **DAGs** page. Find the DAG with the name `postgres_elt_dag`. If the DAG is paused, click on the toggle switch to unpause it and start the ETL process.

Once the DAG is unpaused, it will begin running according to the schedule or when manually triggered.

## Airflow DAGs

This project includes three primary Airflow DAGs that automate the ETL process:

1. **extract_load_csv_to_table_source**:  
   Extracts data from CSV files and loads it into the source PostgreSQL database.
   
2. **extract_load_db_source_to_dwh**:  
   Extracts and loads data from the source database into the staging tables in the Data Warehouse.
   
3. **run_dbt_model**:  
   Executes DBT models to transform the staging data into final tables in the Data Warehouse.

The `extract_load.py` script, located in `dags/common_package/`, handles the extract and load operations. It uses credentials stored in the same folder for connecting to PostgreSQL.

## DBT Setup

DBT is used for transforming the data into a structured format in the Data Warehouse. It also provides jinjja `ref`,`source` to create dependencies and lineage for each run. The `profiles.yml` file is configured for the production environment and connects to the Data Warehouse.

### DBT Profiles

The DBT profiles are configured in the `profiles.yml` file. Here's an example setup:

```
dbt_postgre:
  target: dev
  outputs:
    prod:
      dbname: dev
      host: 172.17.0.1
      pass: pass2021!
      port: 5433
      threads: 1
      type: postgres
      user: dev_user
      schema: public
    dev:
      dbname: dev
      host: 172.17.0.1
      pass: pass2021!
      port: 5433
      threads: 1
      type: postgres
      user: dev_user
      schema: dev
```

This file is essential for connecting your DBT models to the PostgreSQL Data Warehouse. Additionally, a custom macro `get_custom_schema` is provided in the `macros/` directory to allow DBT to use a custom schema for prod configurations (target: prod). You can find the full guide here: [DBT Custom Schema Guide](https://docs.getdbt.com/docs/build/custom-schemas#a-built-in-alternative-pattern-for-generating-schema-names)

```
{% macro generate_schema_name(custom_schema_name, node) -%}
    {{ generate_schema_name_for_env(custom_schema_name, node) }}
{%- endmacro %}
```

### DBT Models

DBT models are stored in the `models/` directory. The models are responsible for transforming the raw data into structured tables in the Data Warehouse. The source tables (`stg_dev_employee`, `stg_dev_performance_rating`) are transformed into the final warehouse tables (`dim_employee`, `fact_employee_performance`).

The models follow the DBT directory structure, with each model containing SQL files that perform transformations on the staging tables. Sources for the models can be found and set up in the `_sources.yml` file.

## Folder Structure

- `asset/csv/`: Contains the raw CSV files (`employee.csv`, `performance_rating.csv`).
- `dags/common_package/`: Contains the common Python scripts like `extract_load.py`.
- `dbt/dbt_postgre/models/`: Stores DBT models used for transforming data.
- `dbt/dbt_postgre/macros/`: Contains custom DBT macros (e.g., `get_custom_schema`).
- `dbt/dbt_postgre/dbt_project.yml`: Configuration file for DBT project settings.
- `dbt/dbt_postgre/profiles.yml`: DBT connection settings for production environment.

## Running the Project

1. **Run Airflow DAGs**:  
   The Airflow DAGs are defined to automate the ETL process. You can trigger the DAGs via the Airflow UI or CLI. Ensure that Airflow is set up correctly and the necessary configurations are in place.
   
   - `extract_load_csv_to_table_source`: Extracts data from CSV files and loads them into PostgreSQL.
   - `extract_load_db_source_to_dwh`: Loads data from PostgreSQL source tables to the Data Warehouse staging tables.
   - `run_dbt_model`: Executes the DBT transformation step.

2. **Run DBT**:  
   After data is loaded into the staging tables, Airflow will start the DBT transformations by triggering the `run_dbt_model` task in Airflow.

## Docker Setup

A custom Docker build is provided to run Apache Airflow and DBT. The `Dockerfile` configures the environment for the ETL process.

### Dockerfile
```
FROM apache/airflow:2.10.4

RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq-dev \
    gcc \
    python3-dev
COPY requirements.txt /
RUN pip install --no-cache-dir "apache-airflow==${AIRFLOW_VERSION}" -r /requirements.txt
```

This Dockerfile installs the necessary dependencies (PostgreSQL client, libpq-dev, GCC, and Python development tools) to run the project in an isolated Docker environment.

To build the Docker image, run:
```
docker-compose build
```

To start the Docker container:
```
docker-compose up -d
```

This will start the Airflow web server and scheduler in the background, and you can access the Airflow UI via `http://localhost:8080`.

## Contribution Guidelines
Feel free to fork this repository and submit pull requests for any improvements, bug fixes, or new features you would like to contribute. Please ensure that your changes are well-documented and tested before submitting.

## License
This project is licensed under the [MIT License](LICENSE).

## Acknowledgements
- **Kaggle** for the HR Analytics dataset that powers this project.
- **Apache Airflow** for workflow automation.
- **DBT (Data Build Tool)** for transforming the data into a meaningful structure in the Data Warehouse.
