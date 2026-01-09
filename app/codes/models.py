"""Codes domain models."""

from datetime import UTC, date, datetime

from app.extensions import db


def utcnow() -> datetime:
    """Return current UTC datetime."""
    return datetime.now(UTC)


class DiscountCode(db.Model):
    """Model for discount codes."""

    __tablename__ = "discount_codes"

    id: int = db.Column(db.Integer, primary_key=True)
    code: str = db.Column(db.String(100), nullable=False)
    store_name: str = db.Column(db.String(200), nullable=False)
    discount_value: str | None = db.Column(db.String(50))
    expiry_date: date | None = db.Column(db.Date)
    notes: str | None = db.Column(db.Text)
    is_used: bool = db.Column(db.Boolean, default=False)
    created_at: datetime = db.Column(db.DateTime, default=utcnow)

    def __repr__(self) -> str:
        """Return string representation of the model."""
        return f"<DiscountCode {self.code} for {self.store_name}>"
