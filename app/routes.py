"""Application routes."""

from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from werkzeug.wrappers import Response
from flask_login import login_required, login_user, logout_user

from app.models import DiscountCode, User, db

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


@main.route("/codes/add", methods=["GET", "POST"])
@login_required
def add_code() -> str | Response:
    """Handle adding a new discount code.

    Returns:
        Rendered add code template or redirect on success.
    """
    if request.method == "POST":
        code = request.form.get("code", "").strip()
        store_name = request.form.get("store_name", "").strip()
        discount_value = request.form.get("discount_value", "").strip() or None
        expiry_date_str = request.form.get("expiry_date", "").strip()
        notes = request.form.get("notes", "").strip() or None

        if not code or not store_name:
            flash("Code and store name are required.", "error")
            return render_template("add_code.html")

        expiry_date = None
        if expiry_date_str:
            try:
                expiry_date = datetime.strptime(expiry_date_str, "%Y-%m-%d").date()
            except ValueError:
                flash("Invalid date format.", "error")
                return render_template("add_code.html")

        discount_code = DiscountCode(
            code=code,
            store_name=store_name,
            discount_value=discount_value,
            expiry_date=expiry_date,
            notes=notes,
        )
        db.session.add(discount_code)
        db.session.commit()

        if request.headers.get("HX-Request"):
            flash("Discount code added successfully!", "success")
            return render_template("partials/add_code_success.html", code=discount_code)

        flash("Discount code added successfully!", "success")
        return redirect(url_for("main.index"))

    return render_template("add_code.html")


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
