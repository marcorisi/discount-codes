"""Tests for codes domain routes."""

from datetime import date, timedelta

from flask.testing import FlaskClient

from app.codes.models import DiscountCode


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


def test_homepage_shows_empty_state(authenticated_client: FlaskClient) -> None:
    """Test homepage shows empty state when no codes exist."""
    response = authenticated_client.get("/")
    assert b"No discount codes yet" in response.data
    assert b"Add your first code" in response.data


def test_homepage_displays_codes(authenticated_client: FlaskClient, db) -> None:
    """Test homepage displays discount codes."""
    code = DiscountCode(code="TEST10", store_name="Test Store", discount_value="10%")
    db.session.add(code)
    db.session.commit()

    response = authenticated_client.get("/")
    assert b"TEST10" in response.data
    assert b"Test Store" in response.data
    assert b"10%" in response.data


def test_homepage_codes_sorted_by_expiry(authenticated_client: FlaskClient, db) -> None:
    """Test homepage displays codes sorted by expiry date ascending."""
    today = date.today()
    code1 = DiscountCode(
        code="LATER",
        store_name="Later Store",
        expiry_date=today + timedelta(days=30),
    )
    code2 = DiscountCode(
        code="SOONER",
        store_name="Sooner Store",
        expiry_date=today + timedelta(days=10),
    )
    code3 = DiscountCode(code="NOEXPIRY", store_name="No Expiry Store")
    db.session.add_all([code1, code2, code3])
    db.session.commit()

    response = authenticated_client.get("/")
    data = response.data.decode()

    sooner_pos = data.find("SOONER")
    later_pos = data.find("LATER")
    noexpiry_pos = data.find("NOEXPIRY")

    assert sooner_pos < later_pos < noexpiry_pos


def test_homepage_shows_expired_codes(authenticated_client: FlaskClient, db) -> None:
    """Test homepage shows expired codes with expired label."""
    yesterday = date.today() - timedelta(days=1)
    code = DiscountCode(
        code="EXPIRED10",
        store_name="Expired Store",
        expiry_date=yesterday,
    )
    db.session.add(code)
    db.session.commit()

    response = authenticated_client.get("/")
    assert b"EXPIRED10" in response.data
    assert b"Expired" in response.data


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
