"""Tests for CLI commands."""

from datetime import date, timedelta
from unittest.mock import patch

import pytest
from click.testing import CliRunner
from flask import Flask

from app import create_app
from app.codes.models import DiscountCode
from app.extensions import db as _db


@pytest.fixture
def app_with_slack_cmd() -> Flask:
    """Create application with SLACK_NOTIFIER_CMD configured."""
    app = create_app("testing")
    app.config["SLACK_NOTIFIER_CMD"] = "echo"
    app.config["REMINDER_DAYS_BEFORE"] = 7
    return app


@pytest.fixture
def app_without_slack_cmd() -> Flask:
    """Create application without SLACK_NOTIFIER_CMD configured."""
    app = create_app("testing")
    app.config["SLACK_NOTIFIER_CMD"] = None
    return app


@pytest.fixture
def db_with_slack(app_with_slack_cmd: Flask):
    """Create database for testing with slack command configured."""
    with app_with_slack_cmd.app_context():
        _db.create_all()
        yield _db
        _db.drop_all()


@pytest.fixture
def test_user_for_cli(db_with_slack):
    """Create a test user for CLI tests."""
    from app.auth.models import User

    user = User(username="cliuser")
    user.set_password("testpassword")
    db_with_slack.session.add(user)
    db_with_slack.session.commit()
    return user


class TestSendExpiryReminders:
    """Tests for send-expiry-reminders CLI command."""

    def test_codes_expiring_within_threshold_are_included(
        self, app_with_slack_cmd: Flask, db_with_slack, test_user_for_cli
    ):
        """Test that codes expiring within threshold trigger notifications."""
        expiry = date.today() + timedelta(days=3)
        code = DiscountCode(
            code="TEST123",
            store_name="Amazon",
            discount_value="20% off",
            expiry_date=expiry,
            is_used=False,
            user_id=test_user_for_cli.id,
        )
        db_with_slack.session.add(code)
        db_with_slack.session.commit()

        runner = CliRunner()
        with patch("subprocess.run") as mock_run:
            result = runner.invoke(
                app_with_slack_cmd.cli, ["send-expiry-reminders"]
            )

        assert result.exit_code == 0
        assert "Sent 1 expiry reminder(s)." in result.output
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert call_args[0] == "echo"
        assert "Amazon" in call_args[1]
        assert "20% off" in call_args[1]

    def test_used_codes_are_excluded(
        self, app_with_slack_cmd: Flask, db_with_slack, test_user_for_cli
    ):
        """Test that used codes do not trigger notifications."""
        expiry = date.today() + timedelta(days=3)
        code = DiscountCode(
            code="USED123",
            store_name="BestBuy",
            discount_value="10% off",
            expiry_date=expiry,
            is_used=True,
            user_id=test_user_for_cli.id,
        )
        db_with_slack.session.add(code)
        db_with_slack.session.commit()

        runner = CliRunner()
        with patch("subprocess.run") as mock_run:
            result = runner.invoke(
                app_with_slack_cmd.cli, ["send-expiry-reminders"]
            )

        assert result.exit_code == 0
        assert "Sent 0 expiry reminder(s)." in result.output
        mock_run.assert_not_called()

    def test_already_expired_codes_are_excluded(
        self, app_with_slack_cmd: Flask, db_with_slack, test_user_for_cli
    ):
        """Test that already expired codes do not trigger notifications."""
        expiry = date.today() - timedelta(days=1)
        code = DiscountCode(
            code="EXPIRED123",
            store_name="Target",
            discount_value="15% off",
            expiry_date=expiry,
            is_used=False,
            user_id=test_user_for_cli.id,
        )
        db_with_slack.session.add(code)
        db_with_slack.session.commit()

        runner = CliRunner()
        with patch("subprocess.run") as mock_run:
            result = runner.invoke(
                app_with_slack_cmd.cli, ["send-expiry-reminders"]
            )

        assert result.exit_code == 0
        assert "Sent 0 expiry reminder(s)." in result.output
        mock_run.assert_not_called()

    def test_codes_without_expiry_date_are_excluded(
        self, app_with_slack_cmd: Flask, db_with_slack, test_user_for_cli
    ):
        """Test that codes without expiry date do not trigger notifications."""
        code = DiscountCode(
            code="NOEXPIRY123",
            store_name="Walmart",
            discount_value="5% off",
            expiry_date=None,
            is_used=False,
            user_id=test_user_for_cli.id,
        )
        db_with_slack.session.add(code)
        db_with_slack.session.commit()

        runner = CliRunner()
        with patch("subprocess.run") as mock_run:
            result = runner.invoke(
                app_with_slack_cmd.cli, ["send-expiry-reminders"]
            )

        assert result.exit_code == 0
        assert "Sent 0 expiry reminder(s)." in result.output
        mock_run.assert_not_called()

    def test_codes_expiring_after_threshold_are_excluded(
        self, app_with_slack_cmd: Flask, db_with_slack, test_user_for_cli
    ):
        """Test that codes expiring after threshold do not trigger notifications."""
        expiry = date.today() + timedelta(days=10)  # Beyond 7-day threshold
        code = DiscountCode(
            code="LATER123",
            store_name="Costco",
            discount_value="25% off",
            expiry_date=expiry,
            is_used=False,
            user_id=test_user_for_cli.id,
        )
        db_with_slack.session.add(code)
        db_with_slack.session.commit()

        runner = CliRunner()
        with patch("subprocess.run") as mock_run:
            result = runner.invoke(
                app_with_slack_cmd.cli, ["send-expiry-reminders"]
            )

        assert result.exit_code == 0
        assert "Sent 0 expiry reminder(s)." in result.output
        mock_run.assert_not_called()

    def test_subprocess_failure_stops_execution_and_returns_error(
        self, app_with_slack_cmd: Flask, db_with_slack, test_user_for_cli
    ):
        """Test that subprocess failure stops execution and returns error."""
        import subprocess

        expiry = date.today() + timedelta(days=3)
        code = DiscountCode(
            code="FAIL123",
            store_name="HomeDepot",
            discount_value="30% off",
            expiry_date=expiry,
            is_used=False,
            user_id=test_user_for_cli.id,
        )
        db_with_slack.session.add(code)
        db_with_slack.session.commit()

        runner = CliRunner()
        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.CalledProcessError(1, "echo")
            result = runner.invoke(
                app_with_slack_cmd.cli, ["send-expiry-reminders"]
            )

        assert result.exit_code == 1
        assert "Error: Failed to send notification" in result.output

    def test_missing_slack_notifier_cmd_shows_error(
        self, app_without_slack_cmd: Flask
    ):
        """Test that missing SLACK_NOTIFIER_CMD shows error message."""
        with app_without_slack_cmd.app_context():
            _db.create_all()

            runner = CliRunner()
            result = runner.invoke(
                app_without_slack_cmd.cli, ["send-expiry-reminders"]
            )

            assert result.exit_code == 1
            assert "Error: SLACK_NOTIFIER_CMD is not configured." in result.output

            _db.drop_all()

    def test_codes_expiring_today_are_included(
        self, app_with_slack_cmd: Flask, db_with_slack, test_user_for_cli
    ):
        """Test that codes expiring today trigger notifications."""
        expiry = date.today()
        code = DiscountCode(
            code="TODAY123",
            store_name="Ebay",
            discount_value="50% off",
            expiry_date=expiry,
            is_used=False,
            user_id=test_user_for_cli.id,
        )
        db_with_slack.session.add(code)
        db_with_slack.session.commit()

        runner = CliRunner()
        with patch("subprocess.run") as mock_run:
            result = runner.invoke(
                app_with_slack_cmd.cli, ["send-expiry-reminders"]
            )

        assert result.exit_code == 0
        assert "Sent 1 expiry reminder(s)." in result.output
        mock_run.assert_called_once()

    def test_codes_expiring_exactly_at_threshold_are_included(
        self, app_with_slack_cmd: Flask, db_with_slack, test_user_for_cli
    ):
        """Test that codes expiring exactly at threshold trigger notifications."""
        expiry = date.today() + timedelta(days=7)  # Exactly at threshold
        code = DiscountCode(
            code="EXACT123",
            store_name="Newegg",
            discount_value="40% off",
            expiry_date=expiry,
            is_used=False,
            user_id=test_user_for_cli.id,
        )
        db_with_slack.session.add(code)
        db_with_slack.session.commit()

        runner = CliRunner()
        with patch("subprocess.run") as mock_run:
            result = runner.invoke(
                app_with_slack_cmd.cli, ["send-expiry-reminders"]
            )

        assert result.exit_code == 0
        assert "Sent 1 expiry reminder(s)." in result.output
        mock_run.assert_called_once()
