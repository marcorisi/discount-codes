"""Application routes."""

from flask import Blueprint, render_template

main = Blueprint("main", __name__)


@main.route("/")
def index() -> str:
    """Render the homepage.

    Returns:
        Rendered homepage template.
    """
    return render_template("index.html")
