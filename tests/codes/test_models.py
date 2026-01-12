"""Tests for codes domain models."""

from datetime import date, datetime, timedelta

from app.auth.models import User
from app.codes.models import DiscountCode


def test_discount_code_creation(db, test_user: User) -> None:
    """Test creating a discount code."""
    code = DiscountCode(
        code="SAVE20",
        store_name="Test Store",
        discount_value="20%",
        user_id=test_user.id,
    )
    db.session.add(code)
    db.session.commit()

    saved_code = db.session.get(DiscountCode, code.id)
    assert saved_code is not None
    assert saved_code.code == "SAVE20"
    assert saved_code.store_name == "Test Store"
    assert saved_code.discount_value == "20%"
    assert saved_code.user_id == test_user.id


def test_discount_code_defaults(db, test_user: User) -> None:
    """Test discount code default values."""
    code = DiscountCode(
        code="TEST10",
        store_name="Another Store",
        user_id=test_user.id,
    )
    db.session.add(code)
    db.session.commit()

    saved_code = db.session.get(DiscountCode, code.id)
    assert saved_code.is_used is False
    assert isinstance(saved_code.created_at, datetime)


def test_discount_code_with_expiry(db, test_user: User) -> None:
    """Test discount code with expiry date."""
    expiry = date(2025, 12, 31)
    code = DiscountCode(
        code="EXPIRE25",
        store_name="Expiring Store",
        expiry_date=expiry,
        user_id=test_user.id,
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


def test_discount_code_with_store_url(db, test_user: User) -> None:
    """Test discount code with store URL."""
    code = DiscountCode(
        code="URL20",
        store_name="URL Store",
        store_url="https://example.com",
        user_id=test_user.id,
    )
    db.session.add(code)
    db.session.commit()

    saved_code = db.session.get(DiscountCode, code.id)
    assert saved_code.store_url == "https://example.com"


def test_discount_code_is_expired_false_when_no_expiry(db, test_user: User) -> None:
    """Test is_expired is False when no expiry date is set."""
    code = DiscountCode(
        code="NOEXP",
        store_name="No Expiry Store",
        user_id=test_user.id,
    )
    db.session.add(code)
    db.session.commit()

    assert code.is_expired is False


def test_discount_code_is_expired_false_when_future(db, test_user: User) -> None:
    """Test is_expired is False when expiry date is in the future."""
    code = DiscountCode(
        code="FUTURE",
        store_name="Future Store",
        expiry_date=date.today() + timedelta(days=7),
        user_id=test_user.id,
    )
    db.session.add(code)
    db.session.commit()

    assert code.is_expired is False


def test_discount_code_is_expired_true_when_past(db, test_user: User) -> None:
    """Test is_expired is True when expiry date is in the past."""
    code = DiscountCode(
        code="PAST",
        store_name="Past Store",
        expiry_date=date.today() - timedelta(days=1),
        user_id=test_user.id,
    )
    db.session.add(code)
    db.session.commit()

    assert code.is_expired is True


def test_discount_code_is_shareable_true_when_valid(db, test_user: User) -> None:
    """Test is_shareable is True for unused, non-expired code."""
    code = DiscountCode(
        code="SHAREABLE",
        store_name="Shareable Store",
        expiry_date=date.today() + timedelta(days=7),
        is_used=False,
        user_id=test_user.id,
    )
    db.session.add(code)
    db.session.commit()

    assert code.is_shareable is True


def test_discount_code_is_shareable_false_when_used(db, test_user: User) -> None:
    """Test is_shareable is False when code is used."""
    code = DiscountCode(
        code="USED",
        store_name="Used Store",
        is_used=True,
        user_id=test_user.id,
    )
    db.session.add(code)
    db.session.commit()

    assert code.is_shareable is False


def test_discount_code_is_shareable_false_when_expired(db, test_user: User) -> None:
    """Test is_shareable is False when code is expired."""
    code = DiscountCode(
        code="EXPIRED",
        store_name="Expired Store",
        expiry_date=date.today() - timedelta(days=1),
        is_used=False,
        user_id=test_user.id,
    )
    db.session.add(code)
    db.session.commit()

    assert code.is_shareable is False


def test_discount_code_user_relationship(db, test_user: User) -> None:
    """Test discount code user relationship."""
    code = DiscountCode(
        code="USERREL",
        store_name="User Rel Store",
        user_id=test_user.id,
    )
    db.session.add(code)
    db.session.commit()

    saved_code = db.session.get(DiscountCode, code.id)
    assert saved_code.user == test_user
    assert saved_code.user.username == "testuser"
