import os
import json
import asyncio
from typing import Optional

from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
from aiokafka.admin import AIOKafkaAdminClient, NewTopic
from aiokafka.structs import TopicPartition

KAFKA_BOOTSTRAP = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")
TOPIC = os.getenv("KAFKA_TOPIC", "sales")

producer: Optional[AIOKafkaProducer] = None
consumer: Optional[AIOKafkaConsumer] = None

async def wait_for_kafka(host: str, port: int, retry_interval: float = 1.0):
    while True:
        try:
            reader, writer = await asyncio.open_connection(host, port)
            writer.close()
            await writer.wait_closed()
            return
        except Exception:
            await asyncio.sleep(retry_interval)

async def init_producer():
    global producer, consumer

    # 1) Дождаться доступности Kafka
    host, port_str = KAFKA_BOOTSTRAP.split(":")
    await wait_for_kafka(host, int(port_str))

    # 2) Запустить продьюсер
    producer = AIOKafkaProducer(bootstrap_servers=KAFKA_BOOTSTRAP)
    await producer.start()

    # 3) Убедиться, что топик существует (создать, если нет)
    admin = AIOKafkaAdminClient(bootstrap_servers=KAFKA_BOOTSTRAP)
    await admin.start()
    try:
        existing = await admin.list_topics()
        if TOPIC not in existing:
            topic = NewTopic(name=TOPIC, num_partitions=5, replication_factor=1)
            await admin.create_topics([topic])
    finally:
        await admin.close()

    # 4) Запустить консьюмер без группы и автокоммита
    consumer = AIOKafkaConsumer(
        bootstrap_servers=KAFKA_BOOTSTRAP,
        group_id=None,
        auto_offset_reset="earliest",
        enable_auto_commit=False,
    )
    await consumer.start()

    # 5) Подождать, пока метаданные по топику появятся
    partitions = None
    while True:
        partitions = consumer.partitions_for_topic(TOPIC)
        if partitions:
            break
        await asyncio.sleep(0.1)

    # 6) Явно назначить все партиции
    tps = [TopicPartition(TOPIC, p) for p in partitions]
    consumer.assign(tps)

    # 7) Переместить курсор на начало
    await consumer.seek_to_beginning(*tps)

    # 8) Восстановить in-memory cache из всех сообщений
    from app.services.sale_service import _sales_store
    from app.models.sale import Sale

    async def rebuild_in_memory_state():
        async for msg in consumer:
            sale_id = int.from_bytes(msg.key, "big")
            if msg.value is None:
                _sales_store.pop(sale_id, None)
            else:
                data = json.loads(msg.value.decode())
                _sales_store[sale_id] = Sale(**data)

    asyncio.create_task(rebuild_in_memory_state())

async def close_producer():
    global producer, consumer
    if producer:
        await producer.stop()
        producer = None
    if consumer:
        await consumer.stop()
        consumer = None
