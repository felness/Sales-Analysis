from fastapi import APIRouter, HTTPException
from model.schemas import ProductCreate, ProductUpdate, ProductResponse
from repository.product import ProductRepository

router = APIRouter()

@router.post("/", response_model=ProductResponse)
async def create_product(product: ProductCreate):
    return await ProductRepository.create(product)

@router.get("/", response_model=list[ProductResponse])
async def read_products(skip: int = 0, limit: int = 10):
    return await ProductRepository.get_all(skip, limit)

@router.get("/{product_id}", response_model=ProductResponse)
async def read_product(product_id: str):
    product = await ProductRepository.get_by_id(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(product_id: str, product: ProductUpdate):
    updated = await ProductRepository.update(product_id, product)
    if not updated:
        raise HTTPException(status_code=404, detail="Product not found")
    return updated

@router.delete("/{product_id}")
async def delete_product(product_id: str):
    deleted = await ProductRepository.delete(product_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted successfully"}