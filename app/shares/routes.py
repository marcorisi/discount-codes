"""Shares domain routes."""

from flask import Blueprint, abort, flash, redirect, render_template, url_for
from flask_login import current_user, login_required
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

    share.visit_count += 1
    db.session.commit()

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

    if not discount_code.is_shareable:
        abort(400)

    share = Share(discount_code_id=discount_code.id, created_by=current_user.id)
    db.session.add(share)
    db.session.commit()

    return redirect(url_for("shares.view_share", token=share.token))


@bp.route("/")
@login_required
def list_shares() -> str:
    """List all shared links created by the current user.

    Returns:
        Rendered list of shared links.
    """
    shares = (
        Share.query.filter_by(created_by=current_user.id)
        .order_by(Share.created_at.desc())
        .all()
    )
    return render_template("shares/list.html", shares=shares)


@bp.route("/<int:share_id>/delete", methods=["POST"])
@login_required
def delete_share(share_id: int) -> Response:
    """Delete a shared link.

    Args:
        share_id: The ID of the share to delete.

    Returns:
        Redirect to the shared links list.
    """
    share = db.get_or_404(Share, share_id)

    if share.created_by != current_user.id:
        abort(403)

    db.session.delete(share)
    db.session.commit()
    flash("Share link deleted.")

    return redirect(url_for("shares.list_shares"))
