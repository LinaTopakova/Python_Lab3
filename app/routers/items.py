from fastapi import APIRouter, HTTPException, Path, Query
from pydantic import BaseModel, Field

# Заглушка базы данных
fake_db = {
    1: {"name": "Foo", "price": 50.2, "is_offer": False},
    2: {"name": "Bar", "price": 30.0, "is_offer": True}
}

class Item(BaseModel):
    name: str = Field(
        ..., 
        title="Название товара", 
        description="Полное название товара (должно быть уникальным)",
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

class ItemUpdate(BaseModel):
    name: str | None = Field(
        None, 
        title="Название товара",
        description="Новое название товара (должно быть уникальным)",
        example="Новый смартфон"
    )
    price: float | None = Field(
        None, 
        gt=0, 
        title="Цена",
        description="Новая цена",
        example=249.99
    )
    is_offer: bool | None = Field(
        None, 
        title="Акционный товар",
        description="Новый статус акции"
    )

router = APIRouter(prefix="/items", tags=["items"])

def is_name_unique(name: str, exclude_id: int | None = None) -> bool:
    for item_id, item_data in fake_db.items():
        if exclude_id and item_id == exclude_id:
            continue
        if item_data["name"].lower() == name.lower():
            return False
    return True

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

@router.post("/", response_model=Item, status_code=201)
def create_item(item: Item):
    
    if not is_name_unique(item.name):
        raise HTTPException(
            status_code=400,
            detail=f"Товар с названием '{item.name}' уже существует"
        )
    
    new_id = max(fake_db.keys()) + 1
    
    fake_db[new_id] = item.model_dump()
    
    return item

@router.put("/{item_id}")
def update_item(
    item_id: int = Path(
        ...,
        title="ID товара",
        description="ID товара для обновления",
        ge=1,
        example=1
    ),
    item_update: ItemUpdate = None
):
    if item_id not in fake_db:
        raise HTTPException(
            status_code=404,
            detail=f"Товар с ID {item_id} не найден"
        )
    
    current_item = fake_db[item_id]
    
    if item_update.name is not None:
        if not is_name_unique(item_update.name, exclude_id=item_id):
            raise HTTPException(
                status_code=400,
                detail=f"Товар с названием '{item_update.name}' уже существует"
            )
        current_item["name"] = item_update.name
    
    if item_update.price is not None:
        current_item["price"] = item_update.price
    
    if item_update.is_offer is not None:
        current_item["is_offer"] = item_update.is_offer
    
    fake_db[item_id] = current_item
    
    return {
        "item_id": item_id,
        "item": current_item,
        "message": "Товар успешно обновлен"
    }

@router.delete("/{item_id}")
def delete_item(
    item_id: int = Path(
        ...,
        title="ID товара",
        description="ID товара для удаления",
        ge=1,
        example=1
    )
):
    
    if item_id not in fake_db:
        raise HTTPException(
            status_code=404,
            detail=f"Товар с ID {item_id} не найден"
        )
    
    deleted_item = fake_db.pop(item_id)
    
    return {
        "message": f"Товар '{deleted_item['name']}' успешно удален",
        "item_id": item_id
    }