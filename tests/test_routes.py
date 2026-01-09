"""Tests for application routes."""

from flask.testing import FlaskClient

from app.models import DiscountCode


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


def test_add_code_page_requires_login(client: FlaskClient, db) -> None:
    """Test add code page redirects to login when not authenticated."""
    response = client.get("/codes/add")
    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


def test_add_code_page_loads(authenticated_client: FlaskClient) -> None:
    """Test add code page loads when authenticated."""
    response = authenticated_client.get("/codes/add")
    assert response.status_code == 200
    assert b"Add Discount Code" in response.data


def test_add_code_with_required_fields(authenticated_client: FlaskClient, db) -> None:
    """Test adding a discount code with required fields only."""
    response = authenticated_client.post(
        "/codes/add",
        data={"code": "SAVE20", "store_name": "Test Store"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Discount code added successfully" in response.data

    code = DiscountCode.query.filter_by(code="SAVE20").first()
    assert code is not None
    assert code.store_name == "Test Store"


def test_add_code_with_all_fields(authenticated_client: FlaskClient, db) -> None:
    """Test adding a discount code with all fields."""
    response = authenticated_client.post(
        "/codes/add",
        data={
            "code": "FULL20",
            "store_name": "Full Store",
            "discount_value": "20%",
            "expiry_date": "2025-12-31",
            "notes": "Test notes",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    code = DiscountCode.query.filter_by(code="FULL20").first()
    assert code is not None
    assert code.discount_value == "20%"
    assert code.notes == "Test notes"


def test_add_code_missing_required_fields(authenticated_client: FlaskClient) -> None:
    """Test adding a discount code with missing required fields."""
    response = authenticated_client.post(
        "/codes/add",
        data={"code": "", "store_name": ""},
        follow_redirects=True,
    )
    assert b"Code and store name are required" in response.data


def test_add_code_invalid_date(authenticated_client: FlaskClient) -> None:
    """Test adding a discount code with invalid date format."""
    response = authenticated_client.post(
        "/codes/add",
        data={
            "code": "INVALID",
            "store_name": "Test Store",
            "expiry_date": "invalid-date",
        },
        follow_redirects=True,
    )
    assert b"Invalid date format" in response.data


def test_add_code_htmx_request(authenticated_client: FlaskClient, db) -> None:
    """Test adding a discount code via HTMX returns partial."""
    response = authenticated_client.post(
        "/codes/add",
        data={"code": "HTMX20", "store_name": "HTMX Store"},
        headers={"HX-Request": "true"},
    )
    assert response.status_code == 200
    assert b"Discount code added successfully" in response.data
    assert b"Add Another" in response.data
