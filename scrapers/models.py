from pydantic import BaseModel
from typing import List


class PropertyData(BaseModel):
    property_id: str
    title: str
    price: float | None = None
    location: str | None = None
    rules: str | None = None
    room_specs: str | None = None
    url: str

class PropertyList(BaseModel):
    properties: List[PropertyData]
