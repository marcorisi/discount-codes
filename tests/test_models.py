"""Tests for database models."""

from datetime import date, datetime

from app.models import DiscountCode


def test_discount_code_creation(db) -> None:
    """Test creating a discount code."""
    code = DiscountCode(
        code="SAVE20",
        store_name="Test Store",
        discount_value="20%",
    )
    db.session.add(code)
    db.session.commit()

    saved_code = db.session.get(DiscountCode, code.id)
    assert saved_code is not None
    assert saved_code.code == "SAVE20"
    assert saved_code.store_name == "Test Store"
    assert saved_code.discount_value == "20%"


def test_discount_code_defaults(db) -> None:
    """Test discount code default values."""
    code = DiscountCode(
        code="TEST10",
        store_name="Another Store",
    )
    db.session.add(code)
    db.session.commit()

    saved_code = db.session.get(DiscountCode, code.id)
    assert saved_code.is_used is False
    assert isinstance(saved_code.created_at, datetime)


def test_discount_code_with_expiry(db) -> None:
    """Test discount code with expiry date."""
    expiry = date(2025, 12, 31)
    code = DiscountCode(
        code="EXPIRE25",
        store_name="Expiring Store",
        expiry_date=expiry,
    )
    db.session.add(code)
    db.session.commit()

    saved_code = db.session.get(DiscountCode, code.id)
    assert saved_code.expiry_date == expiry


def test_discount_code_repr(db) -> None:
    """Test discount code string representation."""
    code = DiscountCode(
        code="REPR10",
        store_name="Repr Store",
    )
    assert repr(code) == "<DiscountCode REPR10 for Repr Store>"
