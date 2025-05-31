CREATE DATABASE IF NOT EXISTS sales_db;

CREATE TABLE sales_db.sales
(
    sale_id UInt32,
    sale_date Date,
    customer_id UInt32,
    seller_id UInt32,
    product_id UInt32,
    sale_quantity UInt32,
    sale_total_price Float64,
    store_name String,
    store_location String,
    store_city String,
    store_state Nullable(String),
    store_country String,
    store_phone String,
    store_email String
)
    ENGINE = MergeTree
PARTITION BY toYYYYMM(sale_date)
ORDER BY (sale_date, store_city, product_id);
