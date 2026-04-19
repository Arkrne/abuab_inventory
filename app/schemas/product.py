from pydantic import BaseModel
from typing import Optional

# This is the strict rulebook for ADDING a new part
class ProductCreate(BaseModel):
    sku: str
    name: str
    category: str
    image_url: Optional[str] = None
    stock_quantity: int
    price: float

# This is what the API is allowed to RETURN to the user
class ProductResponse(ProductCreate):
    id: int

    class Config:
        from_attributes = True

class ProductUpdate(BaseModel):
    stock_quantity: int
    price: float