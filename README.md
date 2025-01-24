Data source: https://www.kaggle.com/datasets/davidafolayan/hr-analytics?select=PerformanceRating.csv

ELT (Extract -> Load -> Transform)

DAG
1. Extract & load data fron CSV to Postgres_1 (Data Source)
2. Extact & load data from Data Source to staging Postgre_2 (Data Lake in Data Warehouse)
3. DBT Transform