"""Codes domain routes."""

from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required
from werkzeug.wrappers import Response

from app.codes.models import DiscountCode
from app.extensions import db

bp = Blueprint("codes", __name__)


@bp.route("/")
@login_required
def index() -> str:
    """Render the homepage.

    Returns:
        Rendered homepage template.
    """
    return render_template("codes/index.html")


@bp.route("/codes/add", methods=["GET", "POST"])
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
            return render_template("codes/add.html")

        expiry_date = None
        if expiry_date_str:
            try:
                expiry_date = datetime.strptime(expiry_date_str, "%Y-%m-%d").date()
            except ValueError:
                flash("Invalid date format.", "error")
                return render_template("codes/add.html")

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
            return render_template("codes/partials/add_success.html", code=discount_code)

        flash("Discount code added successfully!", "success")
        return redirect(url_for("codes.index"))

    return render_template("codes/add.html")
