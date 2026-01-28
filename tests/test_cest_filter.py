"""Tests for the CEST timezone Jinja2 filter."""

from datetime import datetime
from zoneinfo import ZoneInfo

from flask import Flask


def test_cest_filter_converts_utc_to_cest(app: Flask) -> None:
    """Test that the cest filter converts UTC datetimes to Europe/Rome timezone."""
    with app.app_context():
        # Summer time (CEST = UTC+2)
        utc_summer = datetime(2025, 7, 15, 10, 30, tzinfo=ZoneInfo("UTC"))
        result = app.jinja_env.filters["cest"](utc_summer)
        assert result == "Jul 15, 2025 12:30"

        # Winter time (CET = UTC+1)
        utc_winter = datetime(2025, 1, 15, 10, 30, tzinfo=ZoneInfo("UTC"))
        result = app.jinja_env.filters["cest"](utc_winter)
        assert result == "Jan 15, 2025 11:30"


def test_cest_filter_with_custom_format(app: Flask) -> None:
    """Test that the cest filter accepts a custom strftime format."""
    with app.app_context():
        utc_dt = datetime(2025, 7, 15, 10, 30, tzinfo=ZoneInfo("UTC"))
        result = app.jinja_env.filters["cest"](utc_dt, "%B %d, %Y at %H:%M")
        assert result == "July 15, 2025 at 12:30"


def test_cest_filter_handles_naive_datetime(app: Flask) -> None:
    """Test that the cest filter treats naive datetimes as UTC."""
    with app.app_context():
        naive_dt = datetime(2025, 7, 15, 10, 30)
        result = app.jinja_env.filters["cest"](naive_dt)
        assert result == "Jul 15, 2025 12:30"
