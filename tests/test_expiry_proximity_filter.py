"""Tests for the expiry_proximity Jinja2 filter."""

from datetime import date, timedelta

from flask import Flask
from markupsafe import Markup


def _call_filter(app: Flask, expiry_date: date | None) -> Markup:
    """Call the expiry_proximity filter."""
    with app.app_context():
        return app.jinja_env.filters["expiry_proximity"](expiry_date)


def test_returns_empty_for_none(app: Flask) -> None:
    """Test that None expiry date returns empty string."""
    result = _call_filter(app, None)
    assert result == Markup("")


def test_returns_today_when_expiry_is_today(app: Flask) -> None:
    """Test that same-day expiry returns bold '(today)'."""
    today = date.today()
    result = _call_filter(app, today)
    assert result == Markup(" <strong>(today)</strong>")


def test_returns_bold_in_1_day(app: Flask) -> None:
    """Test singular 'day' for 1-day proximity."""
    tomorrow = date.today() + timedelta(days=1)
    result = _call_filter(app, tomorrow)
    assert result == Markup(" <strong>(in 1 day)</strong>")


def test_returns_bold_within_7_days(app: Flask) -> None:
    """Test bold text for expiry within 7 days."""
    expiry = date.today() + timedelta(days=5)
    result = _call_filter(app, expiry)
    assert result == Markup(" <strong>(in 5 days)</strong>")


def test_returns_bold_at_exactly_7_days(app: Flask) -> None:
    """Test bold text at exactly 7 days boundary."""
    expiry = date.today() + timedelta(days=7)
    result = _call_filter(app, expiry)
    assert result == Markup(" <strong>(in 7 days)</strong>")


def test_returns_normal_at_8_days(app: Flask) -> None:
    """Test normal (non-bold) text at 8 days."""
    expiry = date.today() + timedelta(days=8)
    result = _call_filter(app, expiry)
    assert result == Markup(" (in 8 days)")


def test_returns_normal_within_30_days(app: Flask) -> None:
    """Test normal text for expiry within 30 days."""
    expiry = date.today() + timedelta(days=20)
    result = _call_filter(app, expiry)
    assert result == Markup(" (in 20 days)")


def test_returns_normal_at_exactly_30_days(app: Flask) -> None:
    """Test normal text at exactly 30 days boundary."""
    expiry = date.today() + timedelta(days=30)
    result = _call_filter(app, expiry)
    assert result == Markup(" (in 30 days)")


def test_returns_empty_beyond_30_days(app: Flask) -> None:
    """Test empty string for expiry more than 30 days away."""
    expiry = date.today() + timedelta(days=31)
    result = _call_filter(app, expiry)
    assert result == Markup("")


def test_returns_empty_for_expired_date(app: Flask) -> None:
    """Test empty string for already expired date."""
    expired = date.today() - timedelta(days=1)
    result = _call_filter(app, expired)
    assert result == Markup("")
