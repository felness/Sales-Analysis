import os
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from model.models import Product
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "product_db")

async def init_db():
    client = AsyncIOMotorClient(MONGO_URI)
    await init_beanie(
        database=client[MONGO_DB_NAME],
        document_models=[Product]
    )