"""Tests for shares domain models."""

from datetime import datetime, timedelta

from app.auth.models import User
from app.codes.models import DiscountCode
from app.shares.models import Share, generate_token


def test_generate_token_length() -> None:
    """Test token generation creates correct length."""
    token = generate_token()
    assert len(token) == 8


def test_generate_token_alphanumeric() -> None:
    """Test token only contains alphanumeric characters."""
    token = generate_token()
    assert token.isalnum()


def test_generate_token_unique() -> None:
    """Test token generation creates unique tokens."""
    tokens = [generate_token() for _ in range(100)]
    assert len(set(tokens)) == 100


def test_share_creation(db, test_user: User) -> None:
    """Test Share model creation with auto-generated token and expiration."""
    code = DiscountCode(code="TEST10", store_name="Test Store", user_id=test_user.id)
    db.session.add(code)
    db.session.commit()

    share = Share(discount_code_id=code.id)
    db.session.add(share)
    db.session.commit()

    assert share.id is not None
    assert share.token is not None
    assert len(share.token) == 8
    assert share.discount_code_id == code.id
    assert share.expires_at is not None
    assert share.created_at is not None


def test_share_expiration_default_one_day(db, test_user: User) -> None:
    """Test Share expiration defaults to 1 day from creation."""
    code = DiscountCode(code="TEST10", store_name="Test Store", user_id=test_user.id)
    db.session.add(code)
    db.session.commit()

    share = Share(discount_code_id=code.id)
    db.session.add(share)
    db.session.commit()

    expected_expiry = share.created_at + timedelta(days=1)
    # Allow 1 second tolerance for test execution time
    assert abs((share.expires_at - expected_expiry).total_seconds()) < 1


def test_share_is_expired_false_when_valid(db, test_user: User) -> None:
    """Test is_expired returns False for valid share."""
    code = DiscountCode(code="TEST10", store_name="Test Store", user_id=test_user.id)
    db.session.add(code)
    db.session.commit()

    share = Share(discount_code_id=code.id)
    db.session.add(share)
    db.session.commit()

    assert share.is_expired is False


def test_share_is_expired_true_when_expired(db, test_user: User) -> None:
    """Test is_expired returns True for expired share."""
    code = DiscountCode(code="TEST10", store_name="Test Store", user_id=test_user.id)
    db.session.add(code)
    db.session.commit()

    # Create share with past expiration
    share = Share(
        discount_code_id=code.id,
        expires_at=datetime.utcnow() - timedelta(hours=1),
    )
    db.session.add(share)
    db.session.commit()

    assert share.is_expired is True


def test_share_relationship_to_discount_code(db, test_user: User) -> None:
    """Test Share has relationship to DiscountCode."""
    code = DiscountCode(code="TEST10", store_name="Test Store", user_id=test_user.id)
    db.session.add(code)
    db.session.commit()

    share = Share(discount_code_id=code.id)
    db.session.add(share)
    db.session.commit()

    assert share.discount_code == code
    assert share in code.shares


def test_share_repr(db, test_user: User) -> None:
    """Test Share string representation."""
    code = DiscountCode(code="TEST10", store_name="Test Store", user_id=test_user.id)
    db.session.add(code)
    db.session.commit()

    share = Share(discount_code_id=code.id, token="abc12345")
    db.session.add(share)
    db.session.commit()

    assert repr(share) == "<Share abc12345>"


def test_share_token_unique_constraint(db, test_user: User) -> None:
    """Test Share token must be unique."""
    code = DiscountCode(code="TEST10", store_name="Test Store", user_id=test_user.id)
    db.session.add(code)
    db.session.commit()

    share1 = Share(discount_code_id=code.id, token="sametoken")
    db.session.add(share1)
    db.session.commit()

    share2 = Share(discount_code_id=code.id, token="sametoken")
    db.session.add(share2)

    try:
        db.session.commit()
        assert False, "Should have raised an IntegrityError"
    except Exception:
        db.session.rollback()
