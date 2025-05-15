from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from datetime import timedelta
import pymongo
from pyspark.sql import SparkSession
from pyspark.sql.functions import current_date

default_args = {'owner': 'airflow', 'retries': 1, 'retry_delay': timedelta(minutes=5)}

def init_spark():
    return (SparkSession.builder
            .appName("MongoToIceberg")
            .config("spark.jars.packages", "org.apache.iceberg:iceberg-spark-runtime-3.3_2.12:1.3.0")
            .config("spark.sql.catalog.iceberg", "org.apache.iceberg.spark.SparkCatalog")
            .config("spark.sql.catalog.iceberg.type", "hadoop")
            .config("spark.sql.catalog.iceberg.warehouse", "s3a://your-bucket/iceberg/")
            .getOrCreate())

def extract_mongo():
    client = pymongo.MongoClient("mongodb://admin:secret@mongodb:27017/")
    collection = client["product_db"]["your_collection"]
    data = list(collection.find({}))
    for d in data:
        d["_id"] = str(d["_id"])
    return data

def load_mongo_to_iceberg(**kwargs):
    records = kwargs['ti'].xcom_pull(task_ids='extract_mongo')
    spark = init_spark()
    df = spark.createDataFrame(records)
    df = df.withColumn("partition_date", current_date())
    df.write.format("iceberg").mode("append").partitionBy("partition_date").save("iceberg.mongo_ns.product_table")
    spark.stop()

with DAG("mongodb_to_iceberg", default_args=default_args, schedule_interval="@daily", start_date=days_ago(1), catchup=False) as dag:
    extract = PythonOperator(task_id="extract_mongo", python_callable=extract_mongo)
    load = PythonOperator(task_id="load_to_iceberg", python_callable=load_mongo_to_iceberg, provide_context=True)
    extract >> load
