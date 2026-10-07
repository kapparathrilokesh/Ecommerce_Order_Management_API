"""add timestamps

Revision ID: cfd2e5d6f64a
Revises: 812dc0254fb6
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "cfd2e5d6f64a"
down_revision: Union[str, Sequence[str], None] = "812dc0254fb6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    tables = [
        "carts",
        "order_items",
        "orders",
        "payments",
        "products",
        "refunds",
        "returns",
        "reviews",
    ]

    # Add timestamps to tables that have not been modified yet.
    for table in tables:
        op.add_column(
            table,
            sa.Column(
                "created_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
        )

        op.add_column(
            table,
            sa.Column(
                "updated_at",
                sa.DateTime(),
                nullable=False,
                server_default=sa.text("CURRENT_TIMESTAMP"),
            ),
        )

        # Remove the database-level default after existing rows
        # have received their timestamp.
        op.alter_column(
            table,
            "created_at",
            existing_type=sa.DateTime(),
            server_default=None,
        )

        op.alter_column(
            table,
            "updated_at",
            existing_type=sa.DateTime(),
            server_default=None,
        )

    # cart_items already received these columns before the previous
    # migration attempt failed.
    op.alter_column(
        "cart_items",
        "created_at",
        existing_type=sa.DateTime(),
        nullable=False,
        server_default=None,
    )

    op.alter_column(
        "cart_items",
        "updated_at",
        existing_type=sa.DateTime(),
        nullable=False,
        server_default=None,
    )


def downgrade() -> None:
    """Downgrade schema."""

    tables = [
        "reviews",
        "returns",
        "refunds",
        "products",
        "payments",
        "orders",
        "order_items",
        "carts",
        "cart_items",
    ]

    for table in tables:
        op.drop_column(table, "updated_at")
        op.drop_column(table, "created_at")