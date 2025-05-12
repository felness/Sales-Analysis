from fastapi import APIRouter, HTTPException
from typing import List

from app.models.sale import Sale
from app.services.sale_service import SaleService

router = APIRouter(prefix="/sales", tags=["sales"])

@router.get("/", response_model=List[Sale])
async def list_sales():
    return SaleService.list_all()

@router.get("/{sale_id}", response_model=Sale)
async def get_sale(sale_id: int):
    try:
        return SaleService.get(sale_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/", response_model=Sale, status_code=201)
async def create_sale(sale: Sale):
    try:
        return await SaleService.create(sale)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{sale_id}", response_model=Sale)
async def update_sale(sale_id: int, sale: Sale):
    try:
        return await SaleService.update(sale_id, sale)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{sale_id}", status_code=204)
async def delete_sale(sale_id: int):
    try:
        await SaleService.delete(sale_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
