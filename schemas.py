from pydantic import BaseModel
from typing import Optional, List

class ProductItem(BaseModel):
    product: str
    quantity: Optional[int] = 1
    unit: Optional[str] = None
    color: Optional[str] = None
    notes: Optional[str] = None

class ProductList(BaseModel):
    products: List[ProductItem]
