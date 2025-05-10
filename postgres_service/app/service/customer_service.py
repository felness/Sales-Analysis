from typing import List, Optional
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.model.models import Customer
from app.model.schemas import CustomerCreate, CustomerUpdate
from app.repository.customer_repository import (
    get_customer as repo_get_customer,
    get_customers as repo_get_customers,
    create_customer as repo_create_customer,
    update_customer as repo_update_customer,
    delete_customer as repo_delete_customer,
)

async def get_customer(db: AsyncSession, customer_id: int) -> Customer:
    customer = await repo_get_customer(db, customer_id)
    if customer is None:
        raise ValueError(f"Customer with id={customer_id} not found")
    return customer

async def list_customers(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Customer]:
    return await repo_get_customers(db, skip=skip, limit=limit)


async def create_customer(db: AsyncSession, customer_in: CustomerCreate) -> Customer:
    try:
        return await repo_create_customer(db, customer_in)
    except IntegrityError as e:
        raise ValueError(f"Email '{customer_in.email}' is already registered") from e


async def update_customer(db: AsyncSession, customer_id: int, customer_in: CustomerUpdate) -> Customer:
    existing = await repo_get_customer(db, customer_id)
    if existing is None:
        raise ValueError(f"Customer with id={customer_id} not found")
    return await repo_update_customer(db, customer_id, customer_in)


async def delete_customer(db: AsyncSession, customer_id: int) -> None:
    existing = await repo_get_customer(db, customer_id)
    if existing is None:
        raise ValueError(f"Customer with id={customer_id} not found")
    await repo_delete_customer(db, customer_id)
