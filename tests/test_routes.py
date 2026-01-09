"""Tests for application routes."""

from flask.testing import FlaskClient


def test_homepage_status(client: FlaskClient) -> None:
    """Test homepage returns 200 status."""
    response = client.get("/")
    assert response.status_code == 200


def test_homepage_content(client: FlaskClient) -> None:
    """Test homepage contains expected content."""
    response = client.get("/")
    assert b"Discount Code Manager" in response.data
