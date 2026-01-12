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
            "store_url": "https://example.com",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    code = DiscountCode.query.filter_by(code="FULL20").first()
    assert code is not None
    assert code.discount_value == "20%"
    assert code.notes == "Test notes"
    assert code.store_url == "https://example.com"


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


def test_edit_code_page_requires_login(client: FlaskClient, db) -> None:
    """Test edit code page redirects to login when not authenticated."""
    code = DiscountCode(code="TEST10", store_name="Test Store")
    db.session.add(code)
    db.session.commit()

    response = client.get(f"/codes/{code.id}/edit")
    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


def test_edit_code_page_loads(authenticated_client: FlaskClient, db) -> None:
    """Test edit code page loads with prefilled values."""
    code = DiscountCode(
        code="EDIT10",
        store_name="Edit Store",
        discount_value="10%",
        notes="Test notes",
    )
    db.session.add(code)
    db.session.commit()

    response = authenticated_client.get(f"/codes/{code.id}/edit")
    assert response.status_code == 200
    assert b"Edit Discount Code" in response.data
    assert b"EDIT10" in response.data
    assert b"Edit Store" in response.data
    assert b"10%" in response.data
    assert b"Test notes" in response.data


def test_edit_code_page_404_for_nonexistent(authenticated_client: FlaskClient) -> None:
    """Test edit code page returns 404 for nonexistent code."""
    response = authenticated_client.get("/codes/99999/edit")
    assert response.status_code == 404


def test_edit_code_updates_fields(authenticated_client: FlaskClient, db) -> None:
    """Test editing a discount code updates all fields."""
    code = DiscountCode(code="OLD10", store_name="Old Store")
    db.session.add(code)
    db.session.commit()

    response = authenticated_client.post(
        f"/codes/{code.id}/edit",
        data={
            "code": "NEW20",
            "store_name": "New Store",
            "discount_value": "20%",
            "expiry_date": "2025-12-31",
            "notes": "Updated notes",
            "store_url": "https://example.com",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Discount code updated successfully" in response.data

    db.session.refresh(code)
    assert code.code == "NEW20"
    assert code.store_name == "New Store"
    assert code.discount_value == "20%"
    assert code.notes == "Updated notes"
    assert code.store_url == "https://example.com"


def test_edit_code_missing_required_fields(authenticated_client: FlaskClient, db) -> None:
    """Test editing a discount code with missing required fields."""
    code = DiscountCode(code="TEST10", store_name="Test Store")
    db.session.add(code)
    db.session.commit()

    response = authenticated_client.post(
        f"/codes/{code.id}/edit",
        data={"code": "", "store_name": ""},
        follow_redirects=True,
    )
    assert b"Code and store name are required" in response.data


def test_edit_code_invalid_date(authenticated_client: FlaskClient, db) -> None:
    """Test editing a discount code with invalid date format."""
    code = DiscountCode(code="TEST10", store_name="Test Store")
    db.session.add(code)
    db.session.commit()

    response = authenticated_client.post(
        f"/codes/{code.id}/edit",
        data={
            "code": "TEST10",
            "store_name": "Test Store",
            "expiry_date": "invalid-date",
        },
        follow_redirects=True,
    )
    assert b"Invalid date format" in response.data


def test_edit_code_htmx_request(authenticated_client: FlaskClient, db) -> None:
    """Test editing a discount code via HTMX returns partial."""
    code = DiscountCode(code="HTMX10", store_name="HTMX Store")
    db.session.add(code)
    db.session.commit()

    response = authenticated_client.post(
        f"/codes/{code.id}/edit",
        data={"code": "HTMXUPDATED", "store_name": "Updated HTMX Store"},
        headers={"HX-Request": "true"},
    )
    assert response.status_code == 200
    assert b"Discount code updated successfully" in response.data
    assert b"Back to Home" in response.data


def test_homepage_shows_edit_icon(authenticated_client: FlaskClient, db) -> None:
    """Test homepage displays edit icon for each code."""
    code = DiscountCode(code="TEST10", store_name="Test Store")
    db.session.add(code)
    db.session.commit()

    response = authenticated_client.get("/")
    assert f"/codes/{code.id}/edit".encode() in response.data


def test_delete_code_requires_login(client: FlaskClient, db) -> None:
    """Test delete code redirects to login when not authenticated."""
    code = DiscountCode(code="TEST10", store_name="Test Store")
    db.session.add(code)
    db.session.commit()

    response = client.post(f"/codes/{code.id}/delete")
    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


def test_delete_code_removes_code(authenticated_client: FlaskClient, db) -> None:
    """Test deleting a discount code removes it from the database."""
    code = DiscountCode(code="DELETE10", store_name="Delete Store")
    db.session.add(code)
    db.session.commit()
    code_id = code.id

    response = authenticated_client.post(
        f"/codes/{code_id}/delete",
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Discount code deleted successfully" in response.data

    deleted_code = db.session.get(DiscountCode, code_id)
    assert deleted_code is None


def test_delete_code_404_for_nonexistent(authenticated_client: FlaskClient) -> None:
    """Test delete code returns 404 for nonexistent code."""
    response = authenticated_client.post("/codes/99999/delete")
    assert response.status_code == 404


def test_homepage_shows_delete_icon(authenticated_client: FlaskClient, db) -> None:
    """Test homepage displays delete icon for each code."""
    code = DiscountCode(code="TEST10", store_name="Test Store")
    db.session.add(code)
    db.session.commit()

    response = authenticated_client.get("/")
    assert f"/codes/{code.id}/delete".encode() in response.data


def test_homepage_displays_store_url(authenticated_client: FlaskClient, db) -> None:
    """Test homepage displays store URL as a link when present."""
    code = DiscountCode(
        code="URLTEST",
        store_name="URL Store",
        store_url="https://example.com",
    )
    db.session.add(code)
    db.session.commit()

    response = authenticated_client.get("/")
    assert b"https://example.com" in response.data
    assert b"Visit Store" in response.data


# Search and filter tests


def test_homepage_displays_search_form(authenticated_client: FlaskClient) -> None:
    """Test homepage displays search form."""
    response = authenticated_client.get("/")
    assert b'name="search"' in response.data
    assert b'name="expiration"' in response.data
    assert b"Search by store name or URL" in response.data


def test_search_by_store_name(authenticated_client: FlaskClient, db) -> None:
    """Test searching discount codes by store name."""
    code1 = DiscountCode(code="CODE1", store_name="Amazon Store")
    code2 = DiscountCode(code="CODE2", store_name="Target Store")
    db.session.add_all([code1, code2])
    db.session.commit()

    response = authenticated_client.get("/?search=Amazon")
    assert b"CODE1" in response.data
    assert b"Amazon Store" in response.data
    assert b"CODE2" not in response.data


def test_search_by_store_url(authenticated_client: FlaskClient, db) -> None:
    """Test searching discount codes by store URL."""
    code1 = DiscountCode(
        code="CODE1", store_name="Store 1", store_url="https://amazon.com"
    )
    code2 = DiscountCode(
        code="CODE2", store_name="Store 2", store_url="https://target.com"
    )
    db.session.add_all([code1, code2])
    db.session.commit()

    response = authenticated_client.get("/?search=amazon.com")
    assert b"CODE1" in response.data
    assert b"CODE2" not in response.data


def test_search_case_insensitive(authenticated_client: FlaskClient, db) -> None:
    """Test search is case insensitive."""
    code = DiscountCode(code="CODE1", store_name="Amazon Store")
    db.session.add(code)
    db.session.commit()

    response = authenticated_client.get("/?search=amazon")
    assert b"CODE1" in response.data
    assert b"Amazon Store" in response.data


def test_filter_active_codes(authenticated_client: FlaskClient, db) -> None:
    """Test filtering to show only active (non-expired) codes."""
    today = date.today()
    active_code = DiscountCode(
        code="ACTIVE",
        store_name="Active Store",
        expiry_date=today + timedelta(days=10),
    )
    expired_code = DiscountCode(
        code="EXPIRED",
        store_name="Expired Store",
        expiry_date=today - timedelta(days=1),
    )
    no_expiry_code = DiscountCode(code="NOEXPIRY", store_name="No Expiry Store")
    db.session.add_all([active_code, expired_code, no_expiry_code])
    db.session.commit()

    response = authenticated_client.get("/?expiration=active")
    assert b"ACTIVE" in response.data
    assert b"NOEXPIRY" in response.data
    assert b"EXPIRED" not in response.data


def test_filter_expired_codes(authenticated_client: FlaskClient, db) -> None:
    """Test filtering to show only expired codes."""
    today = date.today()
    active_code = DiscountCode(
        code="ACTIVE",
        store_name="Active Store",
        expiry_date=today + timedelta(days=10),
    )
    expired_code = DiscountCode(
        code="EXPIRED",
        store_name="Expired Store",
        expiry_date=today - timedelta(days=1),
    )
    no_expiry_code = DiscountCode(code="NOEXPIRY", store_name="No Expiry Store")
    db.session.add_all([active_code, expired_code, no_expiry_code])
    db.session.commit()

    response = authenticated_client.get("/?expiration=expired")
    assert b"EXPIRED" in response.data
    assert b"ACTIVE" not in response.data
    assert b"NOEXPIRY" not in response.data


def test_search_and_filter_combined(authenticated_client: FlaskClient, db) -> None:
    """Test combining search and expiration filter."""
    today = date.today()
    code1 = DiscountCode(
        code="AMAZON10",
        store_name="Amazon Store",
        expiry_date=today + timedelta(days=10),
    )
    code2 = DiscountCode(
        code="AMAZON20",
        store_name="Amazon Outlet",
        expiry_date=today - timedelta(days=1),
    )
    code3 = DiscountCode(
        code="TARGET10",
        store_name="Target Store",
        expiry_date=today + timedelta(days=10),
    )
    db.session.add_all([code1, code2, code3])
    db.session.commit()

    response = authenticated_client.get("/?search=Amazon&expiration=active")
    assert b"AMAZON10" in response.data
    assert b"AMAZON20" not in response.data
    assert b"TARGET10" not in response.data


def test_search_no_results_message(authenticated_client: FlaskClient, db) -> None:
    """Test empty state message when search returns no results."""
    code = DiscountCode(code="CODE1", store_name="Amazon Store")
    db.session.add(code)
    db.session.commit()

    response = authenticated_client.get("/?search=NonexistentStore")
    assert b"No discount codes match your search criteria" in response.data
    assert b"Clear filters" in response.data


def test_search_preserves_input_value(authenticated_client: FlaskClient) -> None:
    """Test search input preserves the search value after submit."""
    response = authenticated_client.get("/?search=TestSearch")
    assert b'value="TestSearch"' in response.data


def test_filter_preserves_selection(authenticated_client: FlaskClient) -> None:
    """Test expiration filter preserves the selected value after submit."""
    response = authenticated_client.get("/?expiration=active")
    assert b'value="active" selected' in response.data


def test_clear_button_shown_with_filters(authenticated_client: FlaskClient) -> None:
    """Test clear button is shown when filters are applied."""
    response = authenticated_client.get("/?search=test")
    assert b"Clear" in response.data

    response = authenticated_client.get("/?expiration=active")
    assert b"Clear" in response.data


def test_clear_button_hidden_without_filters(authenticated_client: FlaskClient) -> None:
    """Test clear button is hidden when no filters are applied."""
    response = authenticated_client.get("/")
    # Check that Clear button is not present (but Search button is)
    data = response.data.decode()
    assert "Search" in data
    # The Clear link should not be present when no filters
    assert 'class="px-6 py-2 bg-gray-200' not in data


# Mark as used tests


def test_mark_used_requires_login(client: FlaskClient, db) -> None:
    """Test mark used redirects to login when not authenticated."""
    code = DiscountCode(code="TEST10", store_name="Test Store")
    db.session.add(code)
    db.session.commit()

    response = client.post(f"/codes/{code.id}/mark-used")
    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


def test_mark_used_marks_code(authenticated_client: FlaskClient, db) -> None:
    """Test marking a discount code as used updates the database."""
    code = DiscountCode(code="MARKME", store_name="Mark Store", is_used=False)
    db.session.add(code)
    db.session.commit()
    code_id = code.id

    response = authenticated_client.post(
        f"/codes/{code_id}/mark-used",
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Discount code marked as used" in response.data

    db.session.refresh(code)
    assert code.is_used is True


def test_mark_used_404_for_nonexistent(authenticated_client: FlaskClient) -> None:
    """Test mark used returns 404 for nonexistent code."""
    response = authenticated_client.post("/codes/99999/mark-used")
    assert response.status_code == 404


def test_homepage_shows_mark_used_icon_for_unused(
    authenticated_client: FlaskClient, db
) -> None:
    """Test homepage displays mark as used icon for unused codes."""
    code = DiscountCode(code="UNUSED", store_name="Unused Store", is_used=False)
    db.session.add(code)
    db.session.commit()

    response = authenticated_client.get("/")
    assert f"/codes/{code.id}/mark-used".encode() in response.data


def test_homepage_hides_mark_used_icon_for_used(
    authenticated_client: FlaskClient, db
) -> None:
    """Test homepage hides mark as used icon for already used codes."""
    code = DiscountCode(code="USED", store_name="Used Store", is_used=True)
    db.session.add(code)
    db.session.commit()

    response = authenticated_client.get("/")
    assert f"/codes/{code.id}/mark-used".encode() not in response.data


def test_add_code_sets_user_id(authenticated_client: FlaskClient, db) -> None:
    """Test adding a code sets the user_id to the current user."""
    response = authenticated_client.post(
        "/codes/add",
        data={"code": "USER10", "store_name": "User Store"},
        follow_redirects=True,
    )
    assert response.status_code == 200

    code = DiscountCode.query.filter_by(code="USER10").first()
    assert code is not None
    assert code.user_id is not None
    assert code.user is not None
    assert code.user.username == "testuser"


def test_edit_code_updates_user_id(authenticated_client: FlaskClient, db) -> None:
    """Test editing a code updates the user_id to the current user."""
    # Create a code without user_id
    code = DiscountCode(code="NOEDIT", store_name="No Edit Store")
    db.session.add(code)
    db.session.commit()
    assert code.user_id is None

    response = authenticated_client.post(
        f"/codes/{code.id}/edit",
        data={"code": "EDITED", "store_name": "Edited Store"},
        follow_redirects=True,
    )
    assert response.status_code == 200

    db.session.refresh(code)
    assert code.user_id is not None
    assert code.user.username == "testuser"


def test_homepage_displays_edited_by_username(
    authenticated_client: FlaskClient, db
) -> None:
    """Test homepage displays 'edited by username' for codes with user_id."""
    from app.auth.models import User

    user = User.query.filter_by(username="testuser").first()
    code = DiscountCode(code="SHOWUSER", store_name="Show User Store", user_id=user.id)
    db.session.add(code)
    db.session.commit()

    response = authenticated_client.get("/")
    assert b"edited by testuser" in response.data


def test_homepage_hides_edited_by_when_no_user(
    authenticated_client: FlaskClient, db
) -> None:
    """Test homepage hides 'edited by' for codes without user_id."""
    code = DiscountCode(code="NOUSER", store_name="No User Store")
    db.session.add(code)
    db.session.commit()

    response = authenticated_client.get("/")
    assert b"edited by" not in response.data
