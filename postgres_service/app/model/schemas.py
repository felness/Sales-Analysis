'''
pydantic класс валидации запросов и ответов
'''
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field

class CustomerBase(BaseModel):
    first_name: str = Field(..., max_length=50, description="Имя клиента")
    last_name: str = Field(..., max_length=50, description="Фамилия клиента")
    age: Optional[int] = Field(None, ge=0, le=120, description="Возраст клиента (0–120)")
    email: EmailStr = Field(..., description="Рабочий email клиента")
    country: Optional[str] = Field(None, max_length=50, description="Страна проживания")
    postal_code: Optional[str] = Field(None, max_length=20,description="Почтовый индекс")

class SellerBase(BaseModel):
    first_name: str = Field(..., max_length=50, description="Имя продавца")
    last_name: str = Field(..., max_length=50, description="Фамилия продавца")
    email: EmailStr = Field(..., description="Рабочий email продавца")
    country: Optional[str] = Field(None, max_length=50, description="Страна продавца")
    region: Optional[str] = Field(None, max_length=200, description="Регион/область продавца")
    postal_code: Optional[str] = Field(None, max_length=20, description="Почтовый индекс продавца")

# --------- CREATE -----------
class CustomerCreate(CustomerBase):
    pass
class SellerCreate(SellerBase):
    pass

# --------- UPDATE -----------
class CustomerUpdate(BaseModel):
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    age: Optional[int] = Field(None, ge=0, le=120)
    email: Optional[EmailStr] = Field(None)
    country: Optional[str] = Field(None, max_length=50)
    postal_code: Optional[str]= Field(None, max_length=20)

class SellerUpdate(BaseModel):
    first_name: Optional[str] = Field(None, max_length=50)
    last_name: Optional[str] = Field(None, max_length=50)
    email: Optional[EmailStr] = Field(None)
    country: Optional[str] = Field(None, max_length=50)
    region: Optional[str] = Field(None, max_length=200)
    postal_code: Optional[str]= Field(None, max_length=20)

# --------- READ -----------
class CustomerRead(CustomerBase):
    id: int = Field(..., description="Уникальный ID клиента")
    created_at: datetime = Field(..., description="Когда клиент создан в БД")
    class Config:
        orm_mode = True  

class SellerRead(SellerBase):
    id: int = Field(..., description="Уникальный ID продавца")
    created_at: datetime = Field(..., description="Когда продавец создан в БД")

    class Config:
        orm_mode = True