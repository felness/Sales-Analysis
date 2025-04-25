from typing import Optional, List
from bson import ObjectId
from model.models import Product
from model.schemas import ProductResponse, ProductCreate, ProductUpdate
import json

def product_to_response(product: Product) -> ProductResponse:
    product_json = product.model_dump_json(by_alias=True)
    product_dict = json.loads(product_json)
    return ProductResponse.model_validate(product_dict)

class ProductRepository:
    @staticmethod
    async def create(product_data: ProductCreate) -> ProductResponse:
        product = Product(**product_data.model_dump())
        await product.insert()
        return product_to_response(product)

    @staticmethod
    async def get_by_id(product_id: str) -> Optional[ProductResponse]:
        product = await Product.find_one({"_id": ObjectId(product_id)})
        return product_to_response(product) if product else None

    @staticmethod
    async def get_all(skip: int = 0, limit: int = 10) -> List[ProductResponse]:
        products = await Product.find().skip(skip).limit(limit).to_list()
        return [product_to_response(p) for p in products]

    @staticmethod
    async def update(product_id: str, product_data: ProductUpdate) -> Optional[ProductResponse]:
        product = await Product.find_one({"_id": ObjectId(product_id)})
        if product:
            await product.set(product_data.model_dump(exclude_unset=True))
            return product_to_response(product)
        return None

    @staticmethod
    async def delete(product_id: str) -> bool:
        product = await Product.find_one({"_id": ObjectId(product_id)})
        if product:
            await product.delete()
            return True
        return False