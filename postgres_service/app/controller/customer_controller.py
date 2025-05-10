from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.model.schemas import (
    CustomerRead,
    CustomerCreate,
    CustomerUpdate,
)
from app.service.customer_service import (
    get_customer as service_get_customer,
    list_customers as service_list_customers,
    create_customer as service_create_customer,
    update_customer as service_update_customer,
    delete_customer as service_delete_customer,
)

router = APIRouter(
    prefix="/customers",
    tags=["Customers"],
)

@router.get("/", response_model=List[CustomerRead], summary="Список клиентов с пагинацией")
async def read_customers(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db),):
    return await service_list_customers(db, skip=skip, limit=limit)

@router.get("/{customer_id}", response_model=CustomerRead, summary="Получить клиента по ID")
async def read_customer(customer_id: int, db: AsyncSession = Depends(get_db)):
    '''Один клиент по id или 404'''
    try:
        return await service_get_customer(db, customer_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.post("/", response_model=CustomerRead, status_code=status.HTTP_201_CREATED, summary="Создать нового клиента")
async def create_customer(customer_in: CustomerCreate, db: AsyncSession = Depends(get_db),):
    '''Создание клиента, email занят - 404'''
    try:
        return await service_create_customer(db, customer_in)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.patch("/{customer_id}", response_model=CustomerRead, summary="Частичное обновление клиента")
async def patch_customer( customer_id: int, customer_in: CustomerUpdate, db: AsyncSession = Depends(get_db)):
    '''Обновление поля, клиента нет - 404, email дублируется - 400'''
    try:
        return await service_update_customer(db, customer_id, customer_in)
    except ValueError as e:
        code = (
            status.HTTP_404_NOT_FOUND
            if "not found" in str(e)
            else status.HTTP_400_BAD_REQUEST
        )
        raise HTTPException(status_code=code, detail=str(e))


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Удалить клиента")
async def delete_customer(customer_id: int, db: AsyncSession = Depends(get_db)):
    '''Удаление клиента по ID, если его нет - 404'''
    try:
        await service_delete_customer(db, customer_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
