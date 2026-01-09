"""Pytest fixtures for testing."""

import pytest
from flask import Flask
from flask.testing import FlaskClient

from app import create_app
from app.auth.models import User
from app.extensions import db as _db


@pytest.fixture
def app() -> Flask:
    """Create application for testing.

    Returns:
        Flask application configured for testing.
    """
    return create_app("testing")


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    """Create test client.

    Args:
        app: Flask application fixture.

    Returns:
        Flask test client.
    """
    return app.test_client()


@pytest.fixture
def db(app: Flask):
    """Create database for testing.

    Creates all tables before test and drops them after.

    Args:
        app: Flask application fixture.

    Yields:
        SQLAlchemy database instance.
    """
    with app.app_context():
        _db.create_all()
        yield _db
        _db.drop_all()


@pytest.fixture
def test_user(db) -> User:
    """Create a test user.

    Args:
        db: Database fixture.

    Returns:
        Test user instance.
    """
    user = User(username="testuser")
    user.set_password("testpassword")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def authenticated_client(client: FlaskClient, test_user: User) -> FlaskClient:
    """Create an authenticated test client.

    Args:
        client: Flask test client.
        test_user: Test user fixture.

    Returns:
        Authenticated Flask test client.
    """
    client.post(
        "/auth/login",
        data={"username": "testuser", "password": "testpassword"},
        follow_redirects=True,
    )
    return client
