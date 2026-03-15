from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/items", tags=["items"])

class Item(BaseModel):
    name: str
    price: float
    is_offer: bool | None = None

@router.get("/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}

@router.post("/")
def create_item(item: Item):
    return item
