# app/models.py

from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


class ItemStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    ARCHIVED = "archived"


class ItemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(default="", max_length=500)
    price: float = Field(..., gt=0)
    status: ItemStatus = Field(default=ItemStatus.ACTIVE)


class ItemResponse(BaseModel):
    id: str
    name: str
    description: str
    price: float
    status: ItemStatus
    created_at: datetime


class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: datetime


def validate_price_range(price: float, min_price: float = 0.01, max_price: float = 999999.99) -> bool:
    """Validate that price falls within acceptable range."""
    return min_price <= price <= max_price


def format_item_summary(name: str, price: float, status: ItemStatus) -> str:
    """Format a one-line item summary for logging/display."""
    return f"[{status.value.upper()}] {name} - ${price:.2f}"