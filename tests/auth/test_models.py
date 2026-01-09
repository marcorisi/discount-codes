"""Tests for auth domain models."""

from app.auth.models import User


def test_user_creation(db) -> None:
    """Test creating a user."""
    user = User(username="newuser")
    user.set_password("password123")
    db.session.add(user)
    db.session.commit()

    saved_user = db.session.get(User, user.id)
    assert saved_user is not None
    assert saved_user.username == "newuser"


def test_user_password_hashing(db) -> None:
    """Test password is hashed and can be verified."""
    user = User(username="hashtest")
    user.set_password("mypassword")
    db.session.add(user)
    db.session.commit()

    assert user.password_hash != "mypassword"
    assert user.check_password("mypassword") is True
    assert user.check_password("wrongpassword") is False


def test_user_repr(db) -> None:
    """Test user string representation."""
    user = User(username="repruser")
    assert repr(user) == "<User repruser>"
