'''
crud над продавцами
'''
from typing import List, Optional
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.models import Seller
from app.model.schemas import SellerCreate, SellerUpdate

async def get_seller(db: AsyncSession, seller_id: int) -> Optional[Seller]:
    result = await db.execute(
        select(Seller).where(Seller.id == seller_id)
    )
    return result.scalar_one_or_none()

async def get_sellers(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Seller]:
    result = await db.execute(select(Seller).offset(skip).limit(limit))
    return result.scalars().all()

async def create_seller(db: AsyncSession, seller_in: SellerCreate) -> Seller:
    new_seller = Seller(**seller_in.dict())
    db.add(new_seller)
    await db.commit()
    await db.refresh(new_seller)
    return new_seller

async def update_seller(db: AsyncSession, seller_id: int, seller_in: SellerUpdate) -> Optional[Seller]:

    await db.execute(update(Seller)
        .where(Seller.id == seller_id)
        .values(**seller_in.dict(exclude_none=True))
    )
    await db.commit()
    return await get_seller(db, seller_id)

async def delete_seller(db: AsyncSession, seller_id: int) -> None:
    await db.execute(delete(Seller).where(Seller.id == seller_id))
    await db.commit()
