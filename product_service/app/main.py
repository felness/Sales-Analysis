from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import init_db
from controller.product import router as product_controller

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_db_client():
    await init_db()

app.include_router(
    product_controller,
    prefix="/products",
    tags=["products"]
)