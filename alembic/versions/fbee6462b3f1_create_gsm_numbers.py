"""
create: gsm_numbers

Revision ID: fbee6462b3f1
Revises: 3cbd02ce055b
Create Date: 2024-08-25 12:23:28.633571

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "fbee6462b3f1"
down_revision: Union[str, None] = "3cbd02ce055b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "gsm_numbers",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column(
            "poi_id",
            sa.Integer,
            sa.ForeignKey("pois.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("service_provider", sa.String, nullable=False),
        sa.Column("number", sa.String, nullable=False),
        sa.Column("last_call_date", sa.Date, nullable=True),
        sa.Column("last_call_time", sa.Time(timezone=True), nullable=True),
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
    op.drop_table("gsm_numbers")
