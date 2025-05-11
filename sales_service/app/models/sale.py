from datetime import date
from typing import Optional
from pydantic import BaseModel, EmailStr, field_validator, ConfigDict

class Sale(BaseModel):
    sale_id: int
    sale_date: date
    customer_id: int
    seller_id: int
    product_id: int
    sale_quantity: int
    sale_total_price: float
    store_name: str
    store_location: str
    store_city: str
    store_state: Optional[str] = None
    store_country: str
    store_phone: str
    store_email: EmailStr

    model_config = ConfigDict(from_attributes=True)

    @field_validator("sale_date")
    def date_not_in_future(cls, v: date) -> date:
        if v > date.today():
            raise ValueError("Дата продажи не может быть в будущем")
        return v
