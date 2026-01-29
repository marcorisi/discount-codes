"""Flask application factory."""

import shlex
import subprocess
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

import click
from flask import Flask
from markupsafe import Markup

from app.config import config
from app.extensions import db, login_manager, migrate

CEST_TZ = ZoneInfo("Europe/Rome")


@login_manager.user_loader
def load_user(user_id: str):
    """Load user by ID for Flask-Login."""
    from app.auth.models import User

    return db.session.get(User, int(user_id))


def create_app(config_name: str = "default") -> Flask:
    """Create and configure the Flask application.

    Args:
        config_name: Configuration name (development, testing, production, default).

    Returns:
        Configured Flask application instance.
    """
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    from app.auth import bp as auth_bp
    from app.codes import bp as codes_bp
    from app.shares import bp as shares_bp

    app.register_blueprint(codes_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(shares_bp)

    # Add X-Robots-Tag header to all responses
    @app.after_request
    def add_noindex_header(response):
        response.headers['X-Robots-Tag'] = 'noindex, nofollow'
        return response

    @app.route('/robots.txt')
    def robots_txt():
        return app.send_static_file('robots.txt')

    @app.template_filter("cest")
    def cest_filter(dt: datetime, fmt: str = "%b %d, %Y %H:%M") -> str:
        """Convert a UTC datetime to CEST timezone and format it."""
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=ZoneInfo("UTC"))
        return dt.astimezone(CEST_TZ).strftime(fmt)

    @app.template_filter("expiry_proximity")
    def expiry_proximity_filter(expiry_date: date | None) -> Markup:
        """Return an HTML snippet showing how close the expiry date is.

        Returns bold text for ≤7 days, normal text for 8-30 days,
        or empty string if >30 days or no expiry date.
        """
        if expiry_date is None:
            return Markup("")
        days_left = (expiry_date - date.today()).days
        if days_left < 0:
            return Markup("")
        if days_left == 0:
            label = "(today)"
        elif days_left == 1:
            label = "(in 1 day)"
        else:
            label = f"(in {days_left} days)"
        if days_left <= 7:
            return Markup(f' <strong>{label}</strong>')
        if days_left <= 30:
            return Markup(f" {label}")
        return Markup("")

    register_cli_commands(app)

    return app


def register_cli_commands(app: Flask) -> None:
    """Register CLI commands."""
    from app.auth.models import User
    from app.codes.models import DiscountCode

    @app.cli.command("create-user")
    @click.argument("username")
    @click.option("--password", prompt=True, hide_input=True, confirmation_prompt=True)
    def create_user(username: str, password: str) -> None:
        """Create a new user."""
        if User.query.filter_by(username=username).first():
            click.echo(f"Error: User '{username}' already exists.")
            return

        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        click.echo(f"User '{username}' created successfully.")

    @app.cli.command("send-expiry-reminders")
    def send_expiry_reminders() -> None:
        """Send Slack notifications for discount codes expiring soon."""
        cmd = app.config.get("SLACK_NOTIFIER_CMD")
        if not cmd:
            click.echo(f"[{datetime.now().isoformat()}] Error: SLACK_NOTIFIER_CMD is not configured.")
            raise SystemExit(1)

        days_before = app.config.get("REMINDER_DAYS_BEFORE", 7)
        today = date.today()
        threshold_date = today + timedelta(days=days_before)

        codes = DiscountCode.query.filter(
            DiscountCode.is_used == False,  # noqa: E712
            DiscountCode.expiry_date.isnot(None),
            DiscountCode.expiry_date >= today,
            DiscountCode.expiry_date <= threshold_date,
        ).all()

        sent_count = 0
        for code in codes:
            message = (
                f":warning: Reminder: *{code.store_name}* discount code "
                f"*({code.discount_value})* expires on _{code.expiry_date}_!"
            )
            try:
                subprocess.run([*shlex.split(cmd), message], check=True)
                sent_count += 1
            except subprocess.CalledProcessError as e:
                click.echo(f"[{datetime.now().isoformat()}] Error: Failed to send notification: {e}")
                raise SystemExit(1)

        click.echo(f"[{datetime.now().isoformat()}] Sent {sent_count} expiry reminder(s).")


def init_db(app: Flask) -> None:
    """Initialize the database.

    Creates all tables defined in the models.
    Call this function when you need to set up the database.

    Args:
        app: Flask application instance.
    """
    with app.app_context():
        db.create_all()
