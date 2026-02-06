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
    app.config["REMINDER_DAYS_LIST"] = [7, 3]
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

    def test_codes_expiring_at_7_day_threshold_are_included(
        self, app_with_slack_cmd: Flask, db_with_slack, test_user_for_cli
    ):
        """Test that codes expiring at 7-day threshold trigger notifications."""
        expiry = date.today() + timedelta(days=7)
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
        # 7-day reminder uses warning emoji, not urgent
        assert ":warning:" in call_args[1]
        assert "URGENT" not in call_args[1]

    def test_codes_expiring_at_3_day_threshold_are_included_with_urgent(
        self, app_with_slack_cmd: Flask, db_with_slack, test_user_for_cli
    ):
        """Test that codes expiring at 3-day threshold trigger urgent notifications."""
        expiry = date.today() + timedelta(days=3)
        code = DiscountCode(
            code="URGENT123",
            store_name="BestBuy",
            discount_value="30% off",
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
        assert "BestBuy" in call_args[1]
        # 3-day reminder uses rotating_light emoji and URGENT prefix
        assert ":rotating_light:" in call_args[1]
        assert "URGENT" in call_args[1]

    def test_codes_expiring_between_thresholds_are_excluded(
        self, app_with_slack_cmd: Flask, db_with_slack, test_user_for_cli
    ):
        """Test that codes expiring between thresholds do not trigger notifications."""
        # 5 days is between 7 and 3 day thresholds
        expiry = date.today() + timedelta(days=5)
        code = DiscountCode(
            code="BETWEEN123",
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

    def test_used_codes_are_excluded(
        self, app_with_slack_cmd: Flask, db_with_slack, test_user_for_cli
    ):
        """Test that used codes do not trigger notifications."""
        expiry = date.today() + timedelta(days=3)  # At 3-day threshold
        code = DiscountCode(
            code="USED123",
            store_name="Walmart",
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

        expiry = date.today() + timedelta(days=7)  # At 7-day threshold
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

    def test_codes_expiring_today_are_included_when_0_in_thresholds(
        self, app_with_slack_cmd: Flask, db_with_slack, test_user_for_cli
    ):
        """Test that codes expiring today trigger notifications when 0 is in thresholds."""
        app_with_slack_cmd.config["REMINDER_DAYS_LIST"] = [7, 3, 0]
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
        # 0-day (today) uses urgent messaging
        call_args = mock_run.call_args[0][0]
        assert ":rotating_light:" in call_args[1]
        assert "URGENT" in call_args[1]

    def test_multiple_codes_at_different_thresholds_both_notified(
        self, app_with_slack_cmd: Flask, db_with_slack, test_user_for_cli
    ):
        """Test that codes at both 7-day and 3-day thresholds trigger notifications."""
        # Code at 7-day threshold
        code_7day = DiscountCode(
            code="WEEK123",
            store_name="Newegg",
            discount_value="40% off",
            expiry_date=date.today() + timedelta(days=7),
            is_used=False,
            user_id=test_user_for_cli.id,
        )
        # Code at 3-day threshold
        code_3day = DiscountCode(
            code="URGENT456",
            store_name="Amazon",
            discount_value="25% off",
            expiry_date=date.today() + timedelta(days=3),
            is_used=False,
            user_id=test_user_for_cli.id,
        )
        db_with_slack.session.add_all([code_7day, code_3day])
        db_with_slack.session.commit()

        runner = CliRunner()
        with patch("subprocess.run") as mock_run:
            result = runner.invoke(
                app_with_slack_cmd.cli, ["send-expiry-reminders"]
            )

        assert result.exit_code == 0
        assert "Sent 2 expiry reminder(s)." in result.output
        assert mock_run.call_count == 2
        # Check that one call has warning (7-day) and one has urgent (3-day)
        calls = [call[0][0][1] for call in mock_run.call_args_list]
        assert any(":warning:" in call and "Newegg" in call for call in calls)
        assert any(":rotating_light:" in call and "Amazon" in call for call in calls)
