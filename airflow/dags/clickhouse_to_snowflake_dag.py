from airflow import DAG
from airflow.providers.snowflake.operators.snowflake import SnowflakeOperator
from airflow.providers.clickhouse.hooks.clickhouse import ClickHouseHook
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'clickhouse_to_snowflake',
    default_args=default_args,
    description='Export data from ClickHouse to Snowflake',
    schedule_interval='@daily',
    start_date=days_ago(1),
    catchup=False
)

def export_from_clickhouse(table_name, **context):
    ch_hook = ClickHouseHook(clickhouse_conn_id="clickhouse_default")
    rows = ch_hook.get_records(f'SELECT * FROM {table_name}')
    logger.info(f"Fetched {len(rows)} rows from table {table_name}")
    return rows

def load_into_snowflake(data, target_table, **context):
    snowflake_hook = SnowflakeHook(snowflake_conn_id="snowflake_default")
    columns = ", ".join([col.name for col in data[0]])
    values = ', '.join(['%s'] * len(data[0]))
    insert_stmt = f"INSERT INTO {target_table}({columns}) VALUES ({values})"
    snowflake_hook.run(insert_stmt, parameters=data)
    logger.info(f"Loaded {len(data)} rows into table {target_table}")

tables_map = [
    ('dim_customer', 'sales.dim_customer'),
    ('dim_seller', 'sales.dim_seller'),
    ('product_categories', 'sales.product_categories'),
    ('dim_store', 'sales.dim_store'),
    ('dim_supplier', 'sales.dim_supplier'),
    ('dim_products', 'sales.dim_products'),
    ('customer_contact_info', 'sales.customer_contact_info'),
    ('customer_pet_info', 'sales.customer_pet_info'),
    ('seller_contact_info', 'sales.seller_contact_info'),
    ('store_info', 'sales.store_info'),
    ('supplier_info', 'sales.supplier_info'),
    ('product_statistics', 'sales.product_statistics'),
    ('fact_sales', 'sales.fact_sales')
]

for src_table, dst_table in tables_map:
    fetch_task = PythonOperator(
        task_id=f'fetch_{src_table}',
        python_callable=export_from_clickhouse,
        op_kwargs={'table_name': src_table},
        dag=dag
    )

    load_task = PythonOperator(
        task_id=f'load_{dst_table}',
        python_callable=load_into_snowflake,
        templates_dict={
            'data': "{{ ti.xcom_pull(task_ids='" + fetch_task.task_id + "') }}",
            'target_table': dst_table
        },
        dag=dag
    )

    fetch_task >> load_task