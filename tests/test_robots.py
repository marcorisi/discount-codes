"""Tests for SEO blocking (robots.txt, X-Robots-Tag)."""

from flask.testing import FlaskClient


def test_robots_txt_disallows_all(client: FlaskClient) -> None:
    """Test that robots.txt blocks all bots from all paths."""
    response = client.get("/robots.txt")
    assert response.status_code == 200
    text = response.get_data(as_text=True)
    assert "User-agent: *" in text
    assert "Disallow: /" in text


def test_robots_txt_content_type(client: FlaskClient) -> None:
    """Test that robots.txt returns plain text."""
    response = client.get("/robots.txt")
    assert response.content_type == "text/plain; charset=utf-8"


def test_x_robots_tag_header_present(client: FlaskClient) -> None:
    """Test that X-Robots-Tag header is set on responses."""
    response = client.get("/auth/login")
    assert response.headers.get("X-Robots-Tag") == "noindex, nofollow"
