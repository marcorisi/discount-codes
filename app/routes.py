"""Application routes."""

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, login_user, logout_user

from app.models import User

main = Blueprint("main", __name__)
auth = Blueprint("auth", __name__, url_prefix="/auth")


@main.route("/")
@login_required
def index() -> str:
    """Render the homepage.

    Returns:
        Rendered homepage template.
    """
    return render_template("index.html")


@auth.route("/login", methods=["GET", "POST"])
def login():
    """Handle user login."""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Username and password are required.", "error")
            return render_template("login.html")

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get("next")
            return redirect(next_page or url_for("main.index"))

        flash("Invalid username or password.", "error")
    return render_template("login.html")


@auth.route("/logout")
@login_required
def logout():
    """Handle user logout."""
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("auth.login"))
