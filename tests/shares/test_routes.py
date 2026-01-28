"""Tests for shares domain routes."""

from datetime import date, datetime, timedelta, timezone

from flask.testing import FlaskClient

from app.auth.models import User
from app.codes.models import DiscountCode
from app.shares.models import Share


def _get_test_user(db) -> User:
    """Get the test user from the database."""
    return User.query.filter_by(username="testuser").first()


def test_view_share_valid_token(client: FlaskClient, db, test_user: User) -> None:
    """Test viewing a share with valid token shows discount code."""
    code = DiscountCode(
        code="SHARE10",
        store_name="Share Store",
        discount_value="10%",
        notes="Test notes",
        user_id=test_user.id,
    )
    db.session.add(code)
    db.session.commit()

    share = Share(discount_code_id=code.id)
    db.session.add(share)
    db.session.commit()

    response = client.get(f"/shares/{share.token}")
    assert response.status_code == 200
    assert b"Share Store" in response.data
    assert b"SHARE10" in response.data
    assert b"10%" in response.data
    assert b"Test notes" in response.data


def test_view_share_no_auth_required(client: FlaskClient, db, test_user: User) -> None:
    """Test viewing a share does not require authentication."""
    code = DiscountCode(
        code="PUBLIC10",
        store_name="Public Store",
        user_id=test_user.id,
    )
    db.session.add(code)
    db.session.commit()

    share = Share(discount_code_id=code.id)
    db.session.add(share)
    db.session.commit()

    # Using unauthenticated client
    response = client.get(f"/shares/{share.token}")
    assert response.status_code == 200
    assert b"Public Store" in response.data


def test_view_share_expired_shows_message(
    client: FlaskClient, db, test_user: User
) -> None:
    """Test viewing an expired share shows expired message."""
    code = DiscountCode(
        code="EXPIRED10",
        store_name="Expired Store",
        user_id=test_user.id,
    )
    db.session.add(code)
    db.session.commit()

    share = Share(
        discount_code_id=code.id,
        expires_at=datetime.now(timezone.utc) - timedelta(hours=1),
    )
    db.session.add(share)
    db.session.commit()

    response = client.get(f"/shares/{share.token}")
    assert response.status_code == 200
    assert b"Link Expired" in response.data
    assert b"This share link has expired" in response.data


def test_view_share_increments_visit_count(
    client: FlaskClient, db, test_user: User
) -> None:
    """Test viewing a valid share increments visit_count."""
    code = DiscountCode(
        code="VISIT10",
        store_name="Visit Store",
        user_id=test_user.id,
    )
    db.session.add(code)
    db.session.commit()

    share = Share(discount_code_id=code.id)
    db.session.add(share)
    db.session.commit()

    assert share.visit_count == 0

    client.get(f"/shares/{share.token}")
    db.session.refresh(share)
    assert share.visit_count == 1

    client.get(f"/shares/{share.token}")
    db.session.refresh(share)
    assert share.visit_count == 2


def test_view_share_expired_does_not_increment_visit_count(
    client: FlaskClient, db, test_user: User
) -> None:
    """Test viewing an expired share does not increment visit_count."""
    code = DiscountCode(
        code="EXPVISIT10",
        store_name="Expired Visit Store",
        user_id=test_user.id,
    )
    db.session.add(code)
    db.session.commit()

    share = Share(
        discount_code_id=code.id,
        expires_at=datetime.now(timezone.utc) - timedelta(hours=1),
    )
    db.session.add(share)
    db.session.commit()

    client.get(f"/shares/{share.token}")
    db.session.refresh(share)
    assert share.visit_count == 0


def test_view_share_invalid_token_404(client: FlaskClient, db) -> None:
    """Test viewing a share with invalid token returns 404."""
    response = client.get("/shares/invalidtoken")
    assert response.status_code == 404


def test_view_share_shows_store_url(client: FlaskClient, db, test_user: User) -> None:
    """Test share view shows store URL when present."""
    code = DiscountCode(
        code="URL10",
        store_name="URL Store",
        store_url="https://example.com",
        user_id=test_user.id,
    )
    db.session.add(code)
    db.session.commit()

    share = Share(discount_code_id=code.id)
    db.session.add(share)
    db.session.commit()

    response = client.get(f"/shares/{share.token}")
    assert response.status_code == 200
    assert b"https://example.com" in response.data
    assert b"Visit Store" in response.data


def test_create_share_requires_login(client: FlaskClient, db, test_user: User) -> None:
    """Test creating a share redirects to login when not authenticated."""
    code = DiscountCode(
        code="TEST10",
        store_name="Test Store",
        user_id=test_user.id,
    )
    db.session.add(code)
    db.session.commit()

    response = client.post(f"/shares/create/{code.id}")
    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


def test_create_share_creates_share(authenticated_client: FlaskClient, db) -> None:
    """Test creating a share creates a new share record."""
    user = _get_test_user(db)
    code = DiscountCode(
        code="CREATE10",
        store_name="Create Store",
        user_id=user.id,
    )
    db.session.add(code)
    db.session.commit()

    response = authenticated_client.post(
        f"/shares/create/{code.id}",
        follow_redirects=False,
    )
    assert response.status_code == 302

    share = Share.query.filter_by(discount_code_id=code.id).first()
    assert share is not None
    assert f"/shares/{share.token}" in response.headers["Location"]


def test_create_share_redirects_to_share_view(
    authenticated_client: FlaskClient, db
) -> None:
    """Test creating a share redirects to the share view page."""
    user = _get_test_user(db)
    code = DiscountCode(
        code="REDIRECT10",
        store_name="Redirect Store",
        user_id=user.id,
    )
    db.session.add(code)
    db.session.commit()

    response = authenticated_client.post(
        f"/shares/create/{code.id}",
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"Redirect Store" in response.data
    assert b"REDIRECT10" in response.data


def test_create_share_404_for_nonexistent_code(
    authenticated_client: FlaskClient,
) -> None:
    """Test creating a share for nonexistent code returns 404."""
    response = authenticated_client.post("/shares/create/99999")
    assert response.status_code == 404


def test_homepage_shows_share_icon(authenticated_client: FlaskClient, db) -> None:
    """Test homepage displays share icon for shareable codes."""
    user = _get_test_user(db)
    code = DiscountCode(
        code="ICON10",
        store_name="Icon Store",
        user_id=user.id,
    )
    db.session.add(code)
    db.session.commit()

    response = authenticated_client.get("/")
    assert f"/shares/create/{code.id}".encode() in response.data


def test_create_share_400_for_used_code(
    authenticated_client: FlaskClient, db
) -> None:
    """Test creating a share for used code returns 400."""
    user = _get_test_user(db)
    code = DiscountCode(
        code="USED10",
        store_name="Used Store",
        is_used=True,
        user_id=user.id,
    )
    db.session.add(code)
    db.session.commit()

    response = authenticated_client.post(f"/shares/create/{code.id}")
    assert response.status_code == 400


def test_create_share_400_for_expired_code(
    authenticated_client: FlaskClient, db
) -> None:
    """Test creating a share for expired code returns 400."""
    user = _get_test_user(db)
    code = DiscountCode(
        code="EXPIRED10",
        store_name="Expired Store",
        expiry_date=date.today() - timedelta(days=1),
        user_id=user.id,
    )
    db.session.add(code)
    db.session.commit()

    response = authenticated_client.post(f"/shares/create/{code.id}")
    assert response.status_code == 400


def test_homepage_hides_share_icon_for_used_code(
    authenticated_client: FlaskClient, db
) -> None:
    """Test homepage hides share icon for used codes."""
    user = _get_test_user(db)
    code = DiscountCode(
        code="USED10",
        store_name="Used Store",
        is_used=True,
        user_id=user.id,
    )
    db.session.add(code)
    db.session.commit()

    response = authenticated_client.get("/")
    assert f"/shares/create/{code.id}".encode() not in response.data


def test_homepage_hides_share_icon_for_expired_code(
    authenticated_client: FlaskClient, db
) -> None:
    """Test homepage hides share icon for expired codes."""
    user = _get_test_user(db)
    code = DiscountCode(
        code="EXPIRED10",
        store_name="Expired Store",
        expiry_date=date.today() - timedelta(days=1),
        user_id=user.id,
    )
    db.session.add(code)
    db.session.commit()

    response = authenticated_client.get("/")
    assert f"/shares/create/{code.id}".encode() not in response.data
