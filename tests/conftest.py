"""Pytest fixtures for testing."""

import pytest
from flask import Flask
from flask.testing import FlaskClient

from app import create_app
from app.models import db as _db


@pytest.fixture
def app() -> Flask:
    """Create application for testing.

    Returns:
        Flask application configured for testing.
    """
    app = create_app("testing")
    return app


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
