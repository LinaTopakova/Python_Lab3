import logging
from fastapi import APIRouter, HTTPException, Path, Query
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

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
    """Проверяет, уникально ли имя товара."""
    logger.debug(f"Checking uniqueness for name '{name}', exclude_id={exclude_id}")
    for item_id, item_data in fake_db.items():
        if exclude_id and item_id == exclude_id:
            continue
        if item_data["name"].lower() == name.lower():
            logger.info(f"Name '{name}' already exists (item_id={item_id})")
            return False
    logger.debug(f"Name '{name}' is unique")
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
    logger.info(f"GET /items/{item_id} called with q='{q}'")
    
    if item_id not in fake_db:
        logger.warning(f"Item {item_id} not found")
        raise HTTPException(
            status_code=404, 
            detail=f"Товар с ID {item_id} не найден"
        )
    
    logger.info(f"Item {item_id} retrieved successfully")
    return {
        "item_id": item_id, 
        "item": fake_db[item_id], 
        "q": q
    }

@router.post("/", response_model=Item, status_code=201)
def create_item(item: Item):
    """Создать новый товар."""
    logger.info(f"POST /items/ called with data: {item.model_dump()}")
    
    if not is_name_unique(item.name):
        logger.warning(f"Failed to create item: name '{item.name}' already exists")
        raise HTTPException(
            status_code=400,
            detail=f"Товар с названием '{item.name}' уже существует"
        )
    
    new_id = max(fake_db.keys()) + 1
    fake_db[new_id] = item.model_dump()
    logger.info(f"Item created successfully with ID {new_id}")
    
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
    logger.info(f"PUT /items/{item_id} called with data: {item_update.model_dump(exclude_unset=True)}")
    
    if item_id not in fake_db:
        logger.warning(f"Update failed: item {item_id} not found")
        raise HTTPException(
            status_code=404,
            detail=f"Товар с ID {item_id} не найден"
        )
    
    current_item = fake_db[item_id]
    
    if item_update.name is not None:
        if not is_name_unique(item_update.name, exclude_id=item_id):
            logger.warning(f"Update failed: name '{item_update.name}' already exists")
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
    logger.info(f"Item {item_id} updated successfully")
    
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
    logger.info(f"DELETE /items/{item_id} called")
    
    if item_id not in fake_db:
        logger.warning(f"Delete failed: item {item_id} not found")
        raise HTTPException(
            status_code=404,
            detail=f"Товар с ID {item_id} не найден"
        )
    
    deleted_item = fake_db.pop(item_id)
    logger.info(f"Item '{deleted_item['name']}' (ID {item_id}) deleted successfully")
    
    return {
        "message": f"Товар '{deleted_item['name']}' успешно удален",
        "item_id": item_id
    }