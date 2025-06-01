from airflow import DAG
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
    'update_clickhouse_dashboards',
    default_args=default_args,
    description='Update dashboards with aggregated data',
    schedule_interval='0 0 * * *',  
    start_date=days_ago(1),
    catchup=False
)

ch_hook = ClickHouseHook(clickhouse_conn_id="clickhouse_default")



def build_sales_by_product():
    query = """
    TRUNCATE TABLE sales_db.sales_by_product;
    INSERT INTO sales_db.sales_by_product
    SELECT
        p.product_id,
        p.product_name,
        c.category_name,
        SUM(fs.total_amount) AS total_revenue,
        SUM(fs.product_quantity) AS total_quantity,
        AVG(ps.product_rating) AS avg_rating,
        COUNT(ps.product_reviews) AS total_reviews
    FROM fact_sales fs
    LEFT JOIN dim_products p ON fs.product_id = p.product_id
    LEFT JOIN product_categories c ON p.product_category = c.category_id
    LEFT JOIN product_statistics ps ON p.product_id = ps.product_id
    GROUP BY p.product_id, p.product_name, c.category_name
    """
    ch_hook.run(query)

def build_sales_by_customer():
    query = """
    TRUNCATE TABLE sales_db.sales_by_customer;
    INSERT INTO sales_db.sales_by_customer
    SELECT
        cu.customer_id,
        cu.first_name,
        cu.last_name,
        ci.customer_country,
        SUM(fs.total_amount) AS total_amount,
        AVG(fs.total_amount) AS avg_check
    FROM fact_sales fs
    LEFT JOIN dim_customer cu ON fs.customer_id = cu.customer_id
    LEFT JOIN customer_contact_info ci ON cu.customer_id = ci.customer_id
    GROUP BY cu.customer_id, cu.first_name, cu.last_name, ci.customer_country
    """
    ch_hook.run(query)

def build_sales_by_time():
    query = """
    TRUNCATE TABLE sales_db.sales_by_time;
    INSERT INTO sales_db.sales_by_time
    SELECT
        EXTRACT(YEAR FROM fs.sale_date) AS sale_year,
        EXTRACT(MONTH FROM fs.sale_date) AS sale_month,
        SUM(fs.total_amount) AS total_revenue,
        SUM(fs.product_quantity) AS total_quantity,
        AVG(fs.product_quantity) AS avg_order_size
    FROM fact_sales fs
    GROUP BY sale_year, sale_month
    """
    ch_hook.run(query)

def build_sales_by_store():
    query = """
    TRUNCATE TABLE sales_db.sales_by_store;
    INSERT INTO sales_db.sales_by_store
    SELECT
        st.store_id,
        st.store_name,
        st.store_city,
        si.store_country,
        SUM(fs.total_amount) AS total_revenue,
        SUM(fs.product_quantity) AS total_quantity,
        AVG(fs.total_amount) AS avg_check
    FROM fact_sales fs
    LEFT JOIN dim_store st ON fs.store_id = st.store_id
    LEFT JOIN store_info si ON st.store_id = si.store_id
    GROUP BY st.store_id, st.store_name, st.store_city, si.store_country
    """
    ch_hook.run(query)

def build_sales_by_supplier():
    query = """
    TRUNCATE TABLE sales_db.sales_by_supplier;
    INSERT INTO sales_db.sales_by_supplier
    SELECT
        su.supplier_id,
        su.supplier_contact,
        si.supplier_country,
        SUM(fs.total_amount) AS total_revenue,
        AVG(p.product_price) AS avg_product_price,
        SUM(fs.product_quantity) AS total_quantity
    FROM fact_sales fs
    LEFT JOIN dim_supplier su ON fs.supplier_id = su.supplier_id
    LEFT JOIN supplier_info si ON su.supplier_id = si.supplier_id
    LEFT JOIN dim_products p ON fs.product_id = p.product_id
    GROUP BY su.supplier_id, su.supplier_contact, si.supplier_country
    """
    ch_hook.run(query)

def build_product_quality():
    query = """
    TRUNCATE TABLE sales_db.product_quality;
    INSERT INTO sales_db.product_quality
    SELECT
        p.product_id,
        p.product_name,
        AVG(ps.product_rating) AS product_rating,
        COUNT(ps.product_reviews) AS total_reviews,
        SUM(fs.total_amount) AS total_revenue,
        SUM(fs.product_quantity) AS total_quantity
    FROM fact_sales fs
    LEFT JOIN dim_products p ON fs.product_id = p.product_id
    LEFT JOIN product_statistics ps ON p.product_id = ps.product_id
    GROUP BY p.product_id, p.product_name
    """
    ch_hook.run(query)

tasks = []
for func in [build_sales_by_product, build_sales_by_customer, build_sales_by_time, build_sales_by_store, build_sales_by_supplier, build_product_quality]:
    task = PythonOperator(
        task_id=func.__name__.replace('_', '-'),
        python_callable=func,
        dag=dag
    )
    tasks.append(task)

prev_task = None
for task in tasks:
    if prev_task is not None:
        prev_task >> task
    prev_task = task