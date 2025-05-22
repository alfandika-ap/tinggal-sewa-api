from pydantic import BaseModel

class Kost(BaseModel):
    title: str
    address: str = ""
    city: str = ""
    province: str = ""
    description: str = ""
    price: str = ""
    facilities: list[str] = []
    rules: list[str] = []
    contact: str = ""
    url: str

class KostList(BaseModel):
    kosts: list[Kost] = []
    total_count: int = 0