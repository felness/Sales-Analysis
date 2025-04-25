from beanie import Document
from pydantic import Field, ConfigDict
from bson import ObjectId
from typing import Optional

class Product(Document):
    id: ObjectId = Field(default_factory=ObjectId, alias="_id")
    title: str
    description: Optional[str] = None
    amount: Optional[int] = None
    brand: Optional[str] = None
    material: Optional[str] = None
    color: Optional[str] = None
    price: float
    supplier_id: Optional[int] = None
    supplier_name: str
    supplier_contact: Optional[str] = None
    supplier_country: Optional[str] = None

    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        json_encoders={ObjectId: str}
    )

    class Settings:
        name = "products"