from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.model.schemas import (
    SellerRead,
    SellerCreate,
    SellerUpdate,
)
from app.service.seller_service import (
    get_seller as service_get_seller,
    list_sellers as service_list_sellers,
    create_seller as service_create_seller,
    update_seller as service_update_seller,
    delete_seller as service_delete_seller,
)

router = APIRouter(
    prefix="/sellers",
    tags=["Sellers"],
)

@router.get("/", response_model=List[SellerRead], summary="Список продавцов")
async def read_sellers(skip: int = 0, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await service_list_sellers(db, skip=skip, limit=limit)

@router.get("/{seller_id}", response_model=SellerRead, summary="Продавец по ID")
async def read_seller(seller_id: int, db: AsyncSession = Depends(get_db)):
    try:
        return await service_get_seller(db, seller_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

@router.post("/", response_model=SellerRead, status_code=status.HTTP_201_CREATED, summary="Создать продавца")
async def create_seller(seller_in: SellerCreate, db: AsyncSession = Depends(get_db)):
    try:
        return await service_create_seller(db, seller_in)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.patch("/{seller_id}", response_model=SellerRead, summary="Частичное обновление продавца",)
async def patch_seller(seller_id: int, seller_in: SellerUpdate, db: AsyncSession = Depends(get_db)):
    try:
        return await service_update_seller(db, seller_id, seller_in)
    except ValueError as e:
        code = (
            status.HTTP_404_NOT_FOUND
            if "not found" in str(e)
            else status.HTTP_400_BAD_REQUEST
        )
        raise HTTPException(status_code=code, detail=str(e))

@router.delete("/{seller_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Удалить продавца",)
async def delete_seller(seller_id: int, db: AsyncSession = Depends(get_db),):
    try:
        await service_delete_seller(db, seller_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
