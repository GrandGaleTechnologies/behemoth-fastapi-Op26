"""
create: residential_addresses

Revision ID: 2d0a03671d5e
Revises: fbee6462b3f1
Create Date: 2024-08-25 12:26:40.367746

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2d0a03671d5e"
down_revision: Union[str, None] = "fbee6462b3f1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "residential_addresses",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column(
            "poi_id",
            sa.Integer,
            sa.ForeignKey("pois.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("country", sa.String, nullable=False),
        sa.Column("state", sa.String, nullable=False),
        sa.Column("city", sa.String, nullable=False),
        sa.Column("address", sa.String, nullable=True),
        sa.Column("is_deleted", sa.Boolean, server_default=sa.false(), nullable=False),
        sa.Column(
            "edited_at",
            sa.DateTime(timezone=True),
            onupdate=sa.text("now()"),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("residential_addresses")
