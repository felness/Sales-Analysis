CREATE DATABASE IF NOT EXISTS sales_db;

USE sales_db;

DROP TABLE IF EXISTS fact_sales;
DROP TABLE IF EXISTS product_statistics;
DROP TABLE IF EXISTS supplier_info;
DROP TABLE IF EXISTS store_info;
DROP TABLE IF EXISTS seller_contact_info;
DROP TABLE IF EXISTS customer_contact_info;
DROP TABLE IF EXISTS customer_pet_info;
DROP TABLE IF EXISTS dim_products;
DROP TABLE IF EXISTS product_categories;
DROP TABLE IF EXISTS dim_store;
DROP TABLE IF EXISTS dim_supplier;
DROP TABLE IF EXISTS dim_seller;
DROP TABLE IF EXISTS dim_customer;

-- 1. Клиенты
CREATE TABLE dim_customer (
                              customer_id UInt32,
                              first_name String,
                              last_name String,
                              age UInt8
) ENGINE = MergeTree
ORDER BY customer_id;

-- 2. Продавцы
CREATE TABLE dim_seller (
                            seller_id UInt32,
                            seller_first_name String,
                            seller_last_name String
) ENGINE = MergeTree
ORDER BY seller_id;

-- 3. Категории товаров
CREATE TABLE product_categories (
                                    category_id UInt32,
                                    category_name String
) ENGINE = MergeTree
ORDER BY category_id;

-- 4. Магазины
CREATE TABLE dim_store (
                           store_id UInt32,
                           store_name String,
                           store_location String,
                           store_city String
) ENGINE = MergeTree
ORDER BY store_id;

-- 5. Поставщики
CREATE TABLE dim_supplier (
                              supplier_id UInt32,
                              supplier_contact String,
                              supplier_city String,
                              supplier_address String
) ENGINE = MergeTree
ORDER BY supplier_id;

-- 6. Товары
CREATE TABLE dim_products (
                              product_id UInt32,
                              product_name String,
                              product_price Float32,
                              product_category UInt32,
                              pet_category String,
                              product_weight Float32,
                              product_color String,
                              product_size String,
                              product_material String,
                              product_brand String,
                              product_description String
) ENGINE = MergeTree
ORDER BY product_id;

-- 7. Контакты клиентов
CREATE TABLE customer_contact_info (
                                       customer_id UInt32,
                                       customer_email String,
                                       customer_country String,
                                       customer_postal_code String
) ENGINE = MergeTree
ORDER BY customer_id;

-- 8. Питомцы клиентов
CREATE TABLE customer_pet_info (
                                   customer_id UInt32,
                                   pet_type String,
                                   pet_name String,
                                   pet_breed String
) ENGINE = MergeTree
ORDER BY customer_id;

-- 9. Контакты продавцов
CREATE TABLE seller_contact_info (
                                     seller_id UInt32,
                                     seller_email String,
                                     seller_country String,
                                     seller_postal_code String
) ENGINE = MergeTree
ORDER BY seller_id;

-- 10. Информация о магазинах
CREATE TABLE store_info (
                            store_id UInt32,
                            store_state String,
                            store_country String,
                            store_phone String,
                            store_email String
) ENGINE = MergeTree
ORDER BY store_id;

-- 11. Информация о поставщиках
CREATE TABLE supplier_info (
                               supplier_id UInt32,
                               supplier_email String,
                               supplier_phone String,
                               supplier_country String
) ENGINE = MergeTree
ORDER BY supplier_id;

-- 12. Статистика товаров
CREATE TABLE product_statistics (
                                    product_id UInt32,
                                    product_rating Float32,
                                    product_reviews UInt32,
                                    product_release_date Date,
                                    product_expiry_date Date
) ENGINE = MergeTree
ORDER BY product_id;

-- 13. Факты продаж
CREATE TABLE fact_sales (
                            sale_id UInt32,
                            customer_id UInt32,
                            product_id UInt32,
                            seller_id UInt32,
                            store_id UInt32,
                            supplier_id UInt32,
                            sale_date Date,
                            product_quantity UInt32,
                            total_amount Decimal(10,2)
) ENGINE = MergeTree
ORDER BY sale_id;
