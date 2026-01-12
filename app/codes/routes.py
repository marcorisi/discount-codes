"""Codes domain routes."""

from datetime import date, datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import login_required
from werkzeug.wrappers import Response

from app.codes.models import DiscountCode
from app.extensions import db

bp = Blueprint("codes", __name__)


@bp.route("/")
@login_required
def index() -> str:
    """Render the homepage with all discount codes.

    Supports filtering by:
    - search: text search on store_name and store_url
    - expiration: 'all', 'active', or 'expired'

    Returns:
        Rendered homepage template with filtered codes sorted by expiry date.
    """
    search = request.args.get("search", "").strip()
    expiration = request.args.get("expiration", "all")
    today = date.today()

    query = DiscountCode.query

    # Apply text search filter
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            db.or_(
                DiscountCode.store_name.ilike(search_pattern),
                DiscountCode.store_url.ilike(search_pattern),
            )
        )

    # Apply expiration filter
    if expiration == "active":
        query = query.filter(
            db.or_(
                DiscountCode.expiry_date.is_(None),
                DiscountCode.expiry_date >= today,
            )
        )
    elif expiration == "expired":
        query = query.filter(DiscountCode.expiry_date < today)

    codes = query.order_by(DiscountCode.expiry_date.asc().nullslast()).all()

    return render_template(
        "codes/index.html",
        codes=codes,
        today=today,
        search=search,
        expiration=expiration,
    )


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
        store_url = request.form.get("store_url", "").strip() or None

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
            store_url=store_url,
        )
        db.session.add(discount_code)
        db.session.commit()

        if request.headers.get("HX-Request"):
            flash("Discount code added successfully!", "success")
            return render_template("codes/partials/add_success.html", code=discount_code)

        flash("Discount code added successfully!", "success")
        return redirect(url_for("codes.index"))

    return render_template("codes/add.html")


@bp.route("/codes/<int:code_id>/edit", methods=["GET", "POST"])
@login_required
def edit_code(code_id: int) -> str | Response:
    """Handle editing an existing discount code.

    Args:
        code_id: The ID of the discount code to edit.

    Returns:
        Rendered edit code template or redirect on success.
    """
    discount_code = db.get_or_404(DiscountCode, code_id)

    if request.method == "POST":
        code = request.form.get("code", "").strip()
        store_name = request.form.get("store_name", "").strip()
        discount_value = request.form.get("discount_value", "").strip() or None
        expiry_date_str = request.form.get("expiry_date", "").strip()
        notes = request.form.get("notes", "").strip() or None
        store_url = request.form.get("store_url", "").strip() or None

        if not code or not store_name:
            flash("Code and store name are required.", "error")
            return render_template("codes/edit.html", code=discount_code)

        expiry_date = None
        if expiry_date_str:
            try:
                expiry_date = datetime.strptime(expiry_date_str, "%Y-%m-%d").date()
            except ValueError:
                flash("Invalid date format.", "error")
                return render_template("codes/edit.html", code=discount_code)

        discount_code.code = code
        discount_code.store_name = store_name
        discount_code.discount_value = discount_value
        discount_code.expiry_date = expiry_date
        discount_code.notes = notes
        discount_code.store_url = store_url
        db.session.commit()

        if request.headers.get("HX-Request"):
            flash("Discount code updated successfully!", "success")
            return render_template("codes/partials/edit_success.html", code=discount_code)

        flash("Discount code updated successfully!", "success")
        return redirect(url_for("codes.index"))

    return render_template("codes/edit.html", code=discount_code)


@bp.route("/codes/<int:code_id>/delete", methods=["POST"])
@login_required
def delete_code(code_id: int) -> Response:
    """Handle deleting a discount code.

    Args:
        code_id: The ID of the discount code to delete.

    Returns:
        Redirect to homepage on success.
    """
    discount_code = db.get_or_404(DiscountCode, code_id)
    db.session.delete(discount_code)
    db.session.commit()

    flash("Discount code deleted successfully!", "success")
    return redirect(url_for("codes.index"))
