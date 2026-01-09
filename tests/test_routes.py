"""Tests for application routes."""

from flask.testing import FlaskClient


def test_homepage_requires_login(client: FlaskClient, db) -> None:
    """Test homepage redirects to login when not authenticated."""
    response = client.get("/")
    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


def test_homepage_status_authenticated(authenticated_client: FlaskClient) -> None:
    """Test homepage returns 200 status when authenticated."""
    response = authenticated_client.get("/")
    assert response.status_code == 200


def test_homepage_content_authenticated(authenticated_client: FlaskClient) -> None:
    """Test homepage contains expected content when authenticated."""
    response = authenticated_client.get("/")
    assert b"Discount Code Manager" in response.data


def test_login_page_loads(client: FlaskClient, db) -> None:
    """Test login page loads successfully."""
    response = client.get("/auth/login")
    assert response.status_code == 200
    assert b"Login" in response.data


def test_login_with_valid_credentials(client: FlaskClient, test_user) -> None:
    """Test login with valid credentials."""
    response = client.post(
        "/auth/login",
        data={"username": "testuser", "password": "testpassword"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Discount Code Manager" in response.data


def test_login_with_invalid_credentials(client: FlaskClient, test_user) -> None:
    """Test login with invalid credentials."""
    response = client.post(
        "/auth/login",
        data={"username": "testuser", "password": "wrongpassword"},
        follow_redirects=True,
    )
    assert b"Invalid username or password" in response.data


def test_login_with_missing_credentials(client: FlaskClient, db) -> None:
    """Test login with missing credentials."""
    response = client.post(
        "/auth/login",
        data={"username": "", "password": ""},
        follow_redirects=True,
    )
    assert b"Username and password are required" in response.data


def test_logout(authenticated_client: FlaskClient) -> None:
    """Test logout functionality."""
    response = authenticated_client.get("/auth/logout", follow_redirects=True)
    assert response.status_code == 200
    assert b"You have been logged out" in response.data
