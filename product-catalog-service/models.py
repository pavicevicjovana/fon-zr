from pydantic import BaseModel
from typing import Optional

class Variant(BaseModel):
    size: str
    color: str
    sku: str
    stock: int

class ProductCreate(BaseModel):
    name: str
    description: str
    price: float
    category: str
    collection: Optional[str] = None
    images: list[str] = []
    variants: list[Variant] = []
    is_active: bool = True

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    category: Optional[str] = None
    collection: Optional[str] = None
    images: Optional[list[str]] = None
    variants: Optional[list[Variant]] = None
    is_active: Optional[bool] = None

class CategoryCreate(BaseModel):
    name: str
    parent_id: Optional[str] = None