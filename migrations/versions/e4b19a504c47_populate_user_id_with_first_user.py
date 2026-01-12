"""Populate user_id with first user

Revision ID: e4b19a504c47
Revises: 5a40cb7c6d53
Create Date: 2026-01-12 17:16:51.242827

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e4b19a504c47'
down_revision = '5a40cb7c6d53'
branch_labels = None
depends_on = None


def upgrade():
    # Get connection to execute raw SQL
    connection = op.get_bind()

    # Get the first user's ID
    result = connection.execute(sa.text("SELECT id FROM users ORDER BY id LIMIT 1"))
    first_user = result.fetchone()

    if first_user:
        first_user_id = first_user[0]
        # Update all discount_codes with NULL user_id
        connection.execute(
            sa.text("UPDATE discount_codes SET user_id = :user_id WHERE user_id IS NULL"),
            {"user_id": first_user_id}
        )


def downgrade():
    # Set user_id back to NULL (reverting the data migration)
    connection = op.get_bind()
    connection.execute(sa.text("UPDATE discount_codes SET user_id = NULL"))
