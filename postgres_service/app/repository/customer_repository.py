'''
crud над клиентами
'''
from typing import List, Optional
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.models import Customer
from app.model.schemas import CustomerCreate, CustomerUpdate

async def get_customer(db: AsyncSession, customer_id: int) -> Optional[Customer]:
    '''клиент по айди'''
    result = await db.execute(
        select(Customer).where(Customer.id == customer_id)
    )
    return result.scalar_one_or_none()

async def get_customers(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Customer]:
    '''список с пагинацией'''
    result = await db.execute(
        select(Customer).offset(skip).limit(limit)
    )
    return result.scalars().all()

async def create_customer(db: AsyncSession, customer_in: CustomerCreate) -> Customer:
    '''создание нового клиента'''
    new_customer = Customer(**customer_in.dict())
    db.add(new_customer)
    await db.commit()
    await db.refresh(new_customer)  
    return new_customer

async def update_customer(db: AsyncSession, customer_id: int, customer_in: CustomerUpdate) -> Optional[Customer]:
    '''Обновление'''
    await db.execute(update(Customer).where(Customer.id == customer_id).values(**customer_in.dict(exclude_none=True)))
    await db.commit()
    return await get_customer(db, customer_id)

async def delete_customer(db: AsyncSession, customer_id: int) -> None:
    '''удалить клиента'''
    await db.execute(delete(Customer).where(Customer.id == customer_id))
    await db.commit()