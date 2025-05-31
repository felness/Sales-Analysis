# streaming_service/app/main.py

import os
import asyncio
import json
from datetime import datetime
from aiokafka import AIOKafkaConsumer
from clickhouse_driver import Client


KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "sales") 

CLICKHOUSE_HOST = os.getenv("CLICKHOUSE_HOST", "clickhouse-stage")
CLICKHOUSE_PORT = int(os.getenv("CLICKHOUSE_PORT", "9000"))
CLICKHOUSE_DATABASE = os.getenv("CLICKHOUSE_DATABASE", "sales_db")
CLICKHOUSE_USER = os.getenv("CLICKHOUSE_USER", "admin")
CLICKHOUSE_PASSWORD = os.getenv("CLICKHOUSE_PASSWORD", "secret")


async def wait_for_kafka(host: str, port: int, retry_interval: float = 1.0):
    while True:
        try:
            reader, writer = await asyncio.open_connection(host, port)
            writer.close()
            await writer.wait_closed()
            return
        except Exception:
            await asyncio.sleep(retry_interval)


async def consume_and_write_to_clickhouse():
    host, port_str = KAFKA_BOOTSTRAP.split(":")
    await wait_for_kafka(host, int(port_str))

    consumer = AIOKafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BOOTSTRAP,
        group_id=None,
        auto_offset_reset="earliest",
        enable_auto_commit=True,
        key_deserializer=lambda k: int.from_bytes(k, "big") if k is not None else None,
        value_deserializer=lambda v: json.loads(v.decode("utf-8")) if v else None,
    )

    await consumer.start()

    client = Client(
        host=CLICKHOUSE_HOST,
        port=CLICKHOUSE_PORT,
        user=CLICKHOUSE_USER,
        password=CLICKHOUSE_PASSWORD,
        database=CLICKHOUSE_DATABASE,
    )

    try:
        async for msg in consumer:
            sale_id = msg.key     
            data = msg.value     

            if data is None:
                client.execute(
                    "ALTER TABLE sales DELETE WHERE sale_id = %(id)s",
                    {"id": sale_id}
                )
                print(f"[streamer] DELETE sale_id={sale_id} из ClickHouse")
            else:
                sale_date = datetime.strptime(data["sale_date"], "%Y-%m-%d").date()
                
                client.execute(
                    """
                    INSERT INTO sales (
                      sale_id,
                      sale_date,
                      customer_id,
                      seller_id,
                      product_id,
                      sale_quantity,
                      sale_total_price,
                      store_name,
                      store_location,
                      store_city,
                      store_state,
                      store_country,
                      store_phone,
                      store_email
                    ) VALUES
                    """,
                    [
                        [
                            sale_id,
                            sale_date,        
                            data["customer_id"],
                            data["seller_id"],
                            data["product_id"],
                            data["sale_quantity"],
                            data["sale_total_price"],
                            data["store_name"],
                            data["store_location"],
                            data["store_city"],
                            data.get("store_state"),  
                            data["store_country"],
                            data["store_phone"],
                            data["store_email"],
                        ]
                    ],
                )
                print(f"[streamer] INSERT sale_id={sale_id} в ClickHouse")
    finally:
        await consumer.stop()


if __name__ == "__main__":
    asyncio.run(consume_and_write_to_clickhouse())
