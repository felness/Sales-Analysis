from typing import Optional
from model.schemas import ProductCreate, ProductUpdate, ProductResponse
from repository.product import ProductRepository

class ProductService:
    @staticmethod
    async def create_product(product: ProductCreate) -> ProductResponse:
        return await ProductRepository.create(product)

    @staticmethod
    async def get_product(product_id: str) -> Optional[ProductResponse]:
        return await ProductRepository.get_by_id(product_id)

    @staticmethod
    async def get_products(skip: int = 0, limit: int = 10) -> list[ProductResponse]:
        return await ProductRepository.get_all(skip, limit)

    @staticmethod
    async def update_product(product_id: str, product: ProductUpdate) -> Optional[ProductResponse]:
        return await ProductRepository.update(product_id, product)

    @staticmethod
    async def delete_product(product_id: str) -> bool:
        return await ProductRepository.delete(product_id)
