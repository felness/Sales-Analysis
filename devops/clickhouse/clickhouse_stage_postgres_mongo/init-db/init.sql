CREATE TABLE customers  (
    id Int64 PRIMARY KEY AUTO_INCREMENT,
    first_name LowCardinality(String),
    last_name LowCardinality(String),
    age Nullable(Int16),
    email String UNIQUE INDEX(email_hash SHA256(email)),
    country LowCardinality(String),
    postal_code FixedString(20),
    created_at DateTime DEFAULT now()
) ENGINE = ReplacingMergeTree(created_at)
ORDER BY (id);


CREATE TABLE sellers  (
    id Int64 PRIMARY KEY AUTO_INCREMENT,
    first_name LowCardinality(String),
    last_name LowCardinality(String),
    email String UNIQUE INDEX(email_hash SHA256(email)),
    country LowCardinality(String),
    region LowCardinality(String),
    postal_code FixedString(20),
    created_at DateTime DEFAULT now()
) ENGINE = ReplacingMergeTree(created_at)
ORDER BY (id);

CREATE TABLE products  (
    id UUID DEFAULT generateUUIDv4(),
    title String,
    description Nullable(String),
    amount Nullable(UInt32),
    brand Nullable(LowCardinality(String)),
    material Nullable(LowCardinality(String)),
    color Nullable(LowCardinality(String)),
    price Decimal(10, 2), 
    supplier_id Nullable(UInt32),
    supplier_name String,
    supplier_contact Nullable(String),
    supplier_country Nullable(LowCardinality(String)) 
) ENGINE = ReplacingMergeTree(version_column)
PARTITION BY toYYYYMM(created_at)
ORDER BY (id);

