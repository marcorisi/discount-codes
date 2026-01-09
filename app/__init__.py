"""Flask application factory."""

import click
from flask import Flask

from app.config import config
from app.extensions import db, login_manager, migrate


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

    app.register_blueprint(codes_bp)
    app.register_blueprint(auth_bp)

    register_cli_commands(app)

    return app


def register_cli_commands(app: Flask) -> None:
    """Register CLI commands."""
    from app.auth.models import User

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


def init_db(app: Flask) -> None:
    """Initialize the database.

    Creates all tables defined in the models.
    Call this function when you need to set up the database.

    Args:
        app: Flask application instance.
    """
    with app.app_context():
        db.create_all()
