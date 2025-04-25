from pydantic import BaseModel, Field, ConfigDict, field_serializer
from bson import ObjectId
from typing import Optional

class ProductBase(BaseModel):
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

class ProductCreate(ProductBase):
    pass

class ProductUpdate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: str = Field(..., alias="_id")
    
    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True,
        arbitrary_types_allowed=True
    )

    @field_serializer('id')
    def serialize_id(self, id: str, _info):
        return str(id)