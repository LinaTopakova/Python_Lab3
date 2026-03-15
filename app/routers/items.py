from fastapi import APIRouter, HTTPException, Path, Query
from pydantic import BaseModel, Field

# Заглушка базы данных
fake_db = {
    1: {"name": "Foo", "price": 50.2},
    2: {"name": "Bar", "price": 30.0, "is_offer": True}
}

class Item(BaseModel):
    name: str = Field(
        ..., 
        title="Название товара", 
        description="Полное название товара",
        example="Смартфон"
    )
    price: float = Field(
        ..., 
        gt=0, 
        title="Цена", 
        description="Цена в долларах США",
        example=199.99
    )
    is_offer: bool | None = Field(
        None, 
        title="Акционный товар",
        description="True, если товар участвует в акции"
    )

router = APIRouter(prefix="/items", tags=["items"])

@router.get("/{item_id}")
def read_item(
    item_id: int = Path(
        ..., 
        title="ID товара", 
        description="Уникальный идентификатор товара в базе данных",
        ge=1, 
        example=1
    ),
    q: str | None = Query(
        None, 
        title="Поисковый запрос", 
        description="Необязательная строка для поиска",
        max_length=50,
        example="test"
    )
):
    if item_id not in fake_db:
        raise HTTPException(
            status_code=404, 
            detail=f"Товар с ID {item_id} не найден"
        )
    
    return {
        "item_id": item_id, 
        "item": fake_db[item_id], 
        "q": q
    }

@router.post("/", response_model=Item)
def create_item(item: Item):
    return item