import logging
from fastapi import HTTPException
from typing import cast

import app.kafka_client as kafka_client
from aiokafka import AIOKafkaProducer
from app.models.sale import Sale

logger = logging.getLogger(__name__)

class SaleRepository:
    @staticmethod
    def _get_producer() -> AIOKafkaProducer:
        if kafka_client.producer is None:
            logger.error("Kafka producer is not initialized")
            raise HTTPException(status_code=503, detail="Kafka продюсер недоступен")
        return cast(AIOKafkaProducer, kafka_client.producer)

    @staticmethod
    async def save(sale: Sale) -> None:
        p = SaleRepository._get_producer()
        key = sale.sale_id.to_bytes(8, "big", signed=False)
        value = sale.model_dump_json().encode("utf-8")
        await p.send_and_wait(kafka_client.TOPIC, key=key, value=value)
        logger.info("Sale %s sent to Kafka", sale.sale_id)

    @staticmethod
    async def delete(sale_id: int) -> None:
        p = SaleRepository._get_producer()
        key = sale_id.to_bytes(8, "big", signed=False)
        await p.send_and_wait(kafka_client.TOPIC, key=key, value=None)
        logger.info("Sale %s deletion sent to Kafka", sale_id)
