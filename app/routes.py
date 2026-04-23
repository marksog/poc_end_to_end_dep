# app/routes.py

from fastapi import APIRouter, HTTPException
from datetime import datetime, timezone
from uuid import uuid4

from app.models import ItemCreate, ItemResponse, ItemStatus

router = APIRouter(prefix="/api")

# In-memory store — keeps the lab simple, no database dependency
_items: dict[str, ItemResponse] = {}


def get_items_store() -> dict[str, ItemResponse]:
    """Return the items store. Exists as a function so tests can mock/reset it."""
    return _items


@router.post("/items", response_model=ItemResponse, status_code=201)
def create_item(item: ItemCreate) -> ItemResponse:
    item_id = str(uuid4())
    new_item = ItemResponse(
        id=item_id,
        name=item.name,
        description=item.description,
        price=item.price,
        status=item.status,
        created_at=datetime.now(timezone.utc),
    )
    _items[item_id] = new_item
    return new_item


@router.get("/items", response_model=list[ItemResponse])
def list_items(status: ItemStatus | None = None) -> list[ItemResponse]:
    if status:
        return [item for item in _items.values() if item.status == status]
    return list(_items.values())


@router.get("/items/{item_id}", response_model=ItemResponse)
def get_item(item_id: str) -> ItemResponse:
    if item_id not in _items:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")
    return _items[item_id]


@router.delete("/items/{item_id}", status_code=204)
def delete_item(item_id: str) -> None:
    if item_id not in _items:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")
    del _items[item_id]

@router.patch("/items/{item_id}", response_model=ItemResponse)
def update_item_status(item_id: str, status: ItemStatus) -> ItemResponse:
    if item_id not in _items:
        raise HTTPException(status_code=404, detail=f"Item {item_id} not found")
    item = _items[item_id]
    updated = item.model_copy(update={"status": status})
    _items[item_id] = updated
    return updated
