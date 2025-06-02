from airflow import DAG
from airflow.providers.clickhouse.hooks.clickhouse import ClickHouseHook
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from datetime import timedelta
import psycopg2
import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum, count, current_date

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def init_spark():
    return (SparkSession.builder
            .appName("PostgresToClickHouse")
            .config("spark.jars.packages", "org.postgresql:postgresql:42.5.0")
            .getOrCreate())

def extract_postgres_yesterday_data():

    yesterday = (current_date() - 1).alias('yesterday')
    
    conn = psycopg2.connect(host="postgres-db", database="your_db", user="your_user", password="your_password", port=5432)
    sql_query = f"SELECT * FROM your_table WHERE created_at >= '{yesterday}'"
    df = pd.read_sql(sql_query, conn)
    return df.to_dict(orient="records")

def aggregate_and_load_to_clickhouse(**context):

    records = context['task_instance'].xcom_pull(task_ids='extract_postgres_yesterday_data')
    if not records:
        print("Нет новых данных для обработки.")
        return
        
    spark = init_spark()
    df = spark.createDataFrame(records)
    
    aggregated_df = df.groupBy(col("category")).agg(sum("price").alias("total_sales"), count("*").alias("item_count"))
    
    clickhouse_hook = ClickHouseHook(clickhouse_conn_id="clickhouse_default")
    aggregated_df.write.format("clickhouse")\
        .option("table", "postgres_aggregated")\
        .option("database", "default")\
        .mode("overwrite")\
        .save()

with DAG("postgres_to_clickhouse_batch_update", default_args=default_args, schedule_interval="@daily", start_date=days_ago(1), catchup=False) as dag:
    extract = PythonOperator(task_id="extract_postgres_yesterday_data", python_callable=extract_postgres_yesterday_data)
    load = PythonOperator(task_id="aggregate_and_load_to_clickhouse", python_callable=aggregate_and_load_to_clickhouse, provide_context=True)
    extract >> load