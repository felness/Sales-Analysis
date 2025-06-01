from airflow import DAG
from airflow.providers.clickhouse.hooks.clickhouse import ClickHouseHook
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from datetime import timedelta
import pymongo
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum, count, current_date

default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

def init_spark():
    return (SparkSession.builder
            .appName("MongoToClickHouse")
            .config("spark.jars.packages", "org.mongodb.spark:mongo-spark-connector_2.12:3.0.1")
            .getOrCreate())

def extract_mongo_yesterday_data():
    """
    Выбираем только записи за вчерашний день из MongoDB.
    """
    yesterday = (current_date() - 1).alias('yesterday')
    
    # Подключаемся к MongoDB
    client = pymongo.MongoClient("mongodb://admin:secret@mongodb:27017/")
    db = client["product_db"]
    collection = db["your_collection"]
    
    # Фильтруем данные за вчерашний день
    yesterday_data = list(collection.find({"created_at": {"$gte": yesterday}}))
    for doc in yesterday_data:
        doc['_id'] = str(doc['_id'])
    return yesterday_data

def aggregate_and_load_to_clickhouse(**context):
    """
    Собираем данные за вчерашний день, создаём агрегаты и сохраняем в ClickHouse.
    """
    records = context['task_instance'].xcom_pull(task_ids='extract_mongo_yesterday_data')
    if not records:
        print("Нет новых данных для обработки.")
        return
        
    spark = init_spark()
    df = spark.createDataFrame(records)
    
    # Выполняем агрегацию (например, считаем сумму продаж и количество товаров по категориям)
    aggregated_df = df.groupBy(col("category")).agg(sum("price").alias("total_sales"), count("*").alias("item_count"))
    
    # Используем ClickHouse hook для сохранения результата
    clickhouse_hook = ClickHouseHook(clickhouse_conn_id="clickhouse_default")
    clickhouse_hook.run(f"""
        CREATE TABLE IF NOT EXISTS mongo_aggregated (
            category String,
            total_sales Float64,
            item_count UInt64
        ) ENGINE = MergeTree ORDER BY category
    """)
    
    # Пишем агрегированную таблицу в ClickHouse
    aggregated_df.write.format("clickhouse")\
        .option("table", "mongo_aggregated")\
        .option("database", "default")\
        .mode("overwrite")\
        .save()

with DAG("mongo_to_clickhouse_batch_update", default_args=default_args, schedule_interval="@daily", start_date=days_ago(1), catchup=False) as dag:
    extract = PythonOperator(task_id="extract_mongo_yesterday_data", python_callable=extract_mongo_yesterday_data)
    load = PythonOperator(task_id="aggregate_and_load_to_clickhouse", python_callable=aggregate_and_load_to_clickhouse, provide_context=True)
    extract >> load
