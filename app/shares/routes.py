"""Shares domain routes."""

from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import login_required
from werkzeug.wrappers import Response

from app.codes.models import DiscountCode
from app.extensions import db
from app.shares.models import Share

bp = Blueprint("shares", __name__, url_prefix="/shares")


@bp.route("/<token>")
def view_share(token: str) -> str:
    """View a shared discount code.

    This route is public and does not require authentication.

    Args:
        token: The unique share token.

    Returns:
        Rendered share view or expired template.
    """
    share = Share.query.filter_by(token=token).first_or_404()

    if share.is_expired:
        return render_template("shares/expired.html")

    return render_template("shares/view.html", share=share, code=share.discount_code)


@bp.route("/create/<int:code_id>", methods=["POST"])
@login_required
def create_share(code_id: int) -> Response:
    """Create a share link for a discount code.

    Args:
        code_id: The ID of the discount code to share.

    Returns:
        Redirect to the share view page.
    """
    discount_code = db.get_or_404(DiscountCode, code_id)

    share = Share(discount_code_id=discount_code.id)
    db.session.add(share)
    db.session.commit()

    flash("Share link created successfully!", "success")
    return redirect(url_for("shares.view_share", token=share.token))
