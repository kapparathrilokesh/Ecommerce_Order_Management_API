"""add sku and category to products

Revision ID: 4466d804cd94
Revises: 83ca51d935e9
Create Date: 2026-10-06 17:14:27.076066

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "4466d804cd94"
down_revision: Union[str, Sequence[str], None] = "83ca51d935e9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add columns temporarily as nullable
    op.add_column(
        "products",
        sa.Column(
            "sku",
            sa.String(length=100),
            nullable=True
        )
    )

    op.add_column(
        "products",
        sa.Column(
            "category_id",
            sa.Integer(),
            nullable=True
        )
    )

    # Give existing products valid values
    op.execute(
        "UPDATE products SET sku = 'BT-HEAD-001' WHERE id = 1"
    )

    op.execute(
        "UPDATE products SET category_id = 1 WHERE id = 1"
    )

    # Make columns required
    op.alter_column(
        "products",
        "sku",
        existing_type=sa.String(length=100),
        nullable=False
    )

    op.alter_column(
        "products",
        "category_id",
        existing_type=sa.Integer(),
        nullable=False
    )

    # Unique SKU index
    op.create_index(
        "ix_products_sku",
        "products",
        ["sku"],
        unique=True
    )

    # Category foreign key
    op.create_foreign_key(
        "fk_products_category_id_categories",
        "products",
        "categories",
        ["category_id"],
        ["id"]
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_products_category_id_categories",
        "products",
        type_="foreignkey"
    )

    op.drop_index(
        "ix_products_sku",
        table_name="products"
    )

    op.drop_column(
        "products",
        "category_id"
    )

    op.drop_column(
        "products",
        "sku"
    )