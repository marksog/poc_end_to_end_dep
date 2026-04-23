# tests/unit/test_models.py

import pytest
from pydantic import ValidationError

from app.models import (
    ItemCreate,
    ItemStatus,
    validate_price_range,
    format_item_summary,
)


class TestItemCreate:
    """Tests for the ItemCreate Pydantic model validation."""

    def test_valid_item(self):
        item = ItemCreate(name="Widget", price=10.00)
        assert item.name == "Widget"
        assert item.price == 10.00
        assert item.status == ItemStatus.ACTIVE  # default
        assert item.description == ""  # default

    def test_item_with_all_fields(self):
        item = ItemCreate(
            name="Premium Widget",
            description="A premium widget",
            price=99.99,
            status=ItemStatus.INACTIVE,
        )
        assert item.status == ItemStatus.INACTIVE
        assert item.description == "A premium widget"

    def test_empty_name_rejected(self):
        with pytest.raises(ValidationError) as exc_info:
            ItemCreate(name="", price=10.00)
        assert "min_length" in str(exc_info.value) or "String should have at least" in str(exc_info.value)

    def test_name_too_long_rejected(self):
        with pytest.raises(ValidationError):
            ItemCreate(name="x" * 101, price=10.00)

    def test_negative_price_rejected(self):
        with pytest.raises(ValidationError):
            ItemCreate(name="Widget", price=-5.00)

    def test_zero_price_rejected(self):
        with pytest.raises(ValidationError):
            ItemCreate(name="Widget", price=0)

    def test_invalid_status_rejected(self):
        with pytest.raises(ValidationError):
            ItemCreate(name="Widget", price=10.00, status="invalid")


class TestValidatePriceRange:
    """Tests for the price range validation helper."""

    def test_price_in_range(self):
        assert validate_price_range(50.00) is True

    def test_price_at_minimum(self):
        assert validate_price_range(0.01) is True

    def test_price_below_minimum(self):
        assert validate_price_range(0.001) is False

    def test_price_at_maximum(self):
        assert validate_price_range(999999.99) is True

    def test_price_above_maximum(self):
        assert validate_price_range(1000000.00) is False

    def test_custom_range(self):
        assert validate_price_range(50.00, min_price=10.00, max_price=100.00) is True
        assert validate_price_range(5.00, min_price=10.00, max_price=100.00) is False


class TestFormatItemSummary:
    """Tests for the item summary formatter."""

    def test_active_item(self):
        result = format_item_summary("Widget", 29.99, ItemStatus.ACTIVE)
        assert result == "[ACTIVE] Widget - $29.99"

    def test_archived_item(self):
        result = format_item_summary("Old Widget", 5.00, ItemStatus.ARCHIVED)
        assert result == "[ARCHIVED] Old Widget - $5.00"

    def test_price_formatting(self):
        result = format_item_summary("Cheap", 1.5, ItemStatus.ACTIVE)
        assert result == "[ACTIVE] Cheap - $1.50"