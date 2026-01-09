"""Flask application factory."""

from flask import Flask

from app.config import config
from app.models import db


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

    from app.routes import main

    app.register_blueprint(main)

    return app


def init_db(app: Flask) -> None:
    """Initialize the database.

    Creates all tables defined in the models.
    Call this function when you need to set up the database.

    Args:
        app: Flask application instance.
    """
    with app.app_context():
        db.create_all()
