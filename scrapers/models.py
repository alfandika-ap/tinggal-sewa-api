from pydantic import BaseModel

class Kost(BaseModel):
    title: str
    address: str
    city: str
    province: str
    description: str
    price: str
    facilities: str
    rules: str
    contact: str
    url: str

class KostList(BaseModel):
    kosts: list[Kost]