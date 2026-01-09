"""Auth domain routes."""

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required, login_user, logout_user

from app.auth.models import User

bp = Blueprint("auth", __name__, url_prefix="/auth")


@bp.route("/login", methods=["GET", "POST"])
def login():
    """Handle user login."""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Username and password are required.", "error")
            return render_template("auth/login.html")

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            next_page = request.args.get("next")
            return redirect(next_page or url_for("codes.index"))

        flash("Invalid username or password.", "error")
    return render_template("auth/login.html")


@bp.route("/logout")
@login_required
def logout():
    """Handle user logout."""
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("auth.login"))
