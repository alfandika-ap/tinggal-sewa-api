from typing import Optional
from pydantic import BaseModel

class Kost(BaseModel):
    title: str
    address: str
    city: str
    province: str
    description: str
    price: float
    facilities: str
    rules: str
    contact: str
    url: str
    image_url: Optional[str] 
    gender: Optional[str] = None


class KostList(BaseModel):
    kosts: list[Kost]