# app/service/seller_service.py

from typing import List, Optional
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.models import Seller
from app.model.schemas import SellerCreate, SellerUpdate
from app.repository.seller_repository import (
    get_seller as repo_get_seller,
    get_sellers as repo_get_sellers,
    create_seller as repo_create_seller,
    update_seller as repo_update_seller,
    delete_seller as repo_delete_seller,
)


async def get_seller(db: AsyncSession, seller_id: int) -> Seller:
    seller = await repo_get_seller(db, seller_id)
    if seller is None:
        raise ValueError(f"Seller with id={seller_id} not found")
    return seller

async def list_sellers(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Seller]:
    return await repo_get_sellers(db, skip=skip, limit=limit)

async def create_seller(db: AsyncSession, seller_in: SellerCreate) -> Seller:
    try:
        return await repo_create_seller(db, seller_in)
    except IntegrityError as e:
        raise ValueError(f"Email '{seller_in.email}' is already registered") from e

async def update_seller(db: AsyncSession, seller_id: int, seller_in: SellerUpdate) -> Seller:
    existing = await repo_get_seller(db, seller_id)
    if existing is None:
        raise ValueError(f"Seller with id={seller_id} not found")
    return await repo_update_seller(db, seller_id, seller_in)

async def delete_seller(db: AsyncSession, seller_id: int) -> None:
    existing = await repo_get_seller(db, seller_id)
    if existing is None:
        raise ValueError(f"Seller with id={seller_id} not found")
    await repo_delete_seller(db, seller_id)
