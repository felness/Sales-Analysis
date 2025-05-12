import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.kafka_client import init_producer, close_producer
from app.controllers.sale_controller import router as sale_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Kafka producer…")
    await init_producer()
    yield
    logger.info("Stopping Kafka producer…")
    await close_producer()

app = FastAPI(lifespan=lifespan)
app.include_router(sale_router)
