from fastapi import FastAPI
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine  
from app.database import get_db 
from app.model.models import Base  
from app.controller.customer_controller import router as customer_router
from app.controller.seller_controller import router as seller_router

load_dotenv(override=True)

app = FastAPI(
    title="Postgres Service",
    description="Микросервис клиенты + продавцы",
    version="1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn: 
        await conn.run_sync(Base.metadata.create_all)

app.include_router(customer_router)
app.include_router(seller_router)

@app.get("/health", summary="Проверка состояние")
async def health():
    return {"status": "ok"}
