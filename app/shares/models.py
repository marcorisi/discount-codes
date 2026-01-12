"""Shares domain models."""

import secrets
import string
from datetime import datetime, timedelta

from app.extensions import db


def utcnow() -> datetime:
    """Return the current UTC time."""
    return datetime.utcnow()


def generate_token(length: int = 8) -> str:
    """Generate a random alphanumeric token.

    Args:
        length: The length of the token to generate.

    Returns:
        A random alphanumeric string.
    """
    alphabet = string.ascii_letters + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(length))


class Share(db.Model):
    """Model for shared discount code links."""

    __tablename__ = "shares"

    id: int = db.Column(db.Integer, primary_key=True)
    token: str = db.Column(db.String(16), unique=True, nullable=False)
    discount_code_id: int = db.Column(
        db.Integer, db.ForeignKey("discount_codes.id"), nullable=False
    )
    created_at: datetime = db.Column(db.DateTime, default=utcnow)
    expires_at: datetime = db.Column(db.DateTime, nullable=False)

    discount_code = db.relationship("DiscountCode", backref="shares")

    def __init__(self, **kwargs) -> None:
        """Initialize a Share with auto-generated token and expiration."""
        if "token" not in kwargs:
            kwargs["token"] = generate_token()
        if "expires_at" not in kwargs:
            kwargs["expires_at"] = utcnow() + timedelta(days=1)
        super().__init__(**kwargs)

    @property
    def is_expired(self) -> bool:
        """Check if the share link has expired."""
        return utcnow() > self.expires_at

    def __repr__(self) -> str:
        """Return string representation of Share."""
        return f"<Share {self.token}>"
