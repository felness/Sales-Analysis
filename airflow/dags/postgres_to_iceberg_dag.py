from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from datetime import timedelta
import psycopg2
import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql.functions import current_date

default_args = {'owner': 'airflow', 'retries': 1, 'retry_delay': timedelta(minutes=5)}

def init_spark():
    return (SparkSession.builder
            .appName("PostgresToIceberg")
            .config("spark.jars.packages", "org.apache.iceberg:iceberg-spark-runtime-3.3_2.12:1.3.0,org.postgresql:postgresql:42.5.0")
            .config("spark.sql.catalog.iceberg", "org.apache.iceberg.spark.SparkCatalog")
            .config("spark.sql.catalog.iceberg.type", "hadoop")
            .config("spark.sql.catalog.iceberg.warehouse", "s3a://your-bucket/iceberg/")
            .getOrCreate())

def extract_postgres():
    conn = psycopg2.connect(
        host="postgres-db",
        database="your_db",
        user="your_user",
        password="your_password",
        port=5432
    )
    df = pd.read_sql("SELECT * FROM your_table;", conn)
    return df.to_dict(orient="records")

def load_postgres_to_iceberg(**kwargs):
    records = kwargs['ti'].xcom_pull(task_ids='extract_postgres')
    spark = init_spark()
    df = spark.createDataFrame(records)
    df = df.withColumn("partition_date", current_date())
    df.write.format("iceberg").mode("append").partitionBy("partition_date").save("iceberg.postgres_ns.my_table")
    spark.stop()

with DAG("postgres_to_iceberg", default_args=default_args, schedule_interval="@daily", start_date=days_ago(1), catchup=False) as dag:
    extract = PythonOperator(task_id="extract_postgres", python_callable=extract_postgres)
    load = PythonOperator(task_id="load_to_iceberg", python_callable=load_postgres_to_iceberg, provide_context=True)
    extract >> load
