"""
create: known_associates

Revision ID: 0fad53da18eb
Revises: 2d0a03671d5e
Create Date: 2024-08-25 12:29:27.232404

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0fad53da18eb"
down_revision: Union[str, None] = "2d0a03671d5e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "known_associates",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column(
            "poi_id",
            sa.Integer,
            sa.ForeignKey("pois.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("full_name", sa.String, nullable=False),
        sa.Column("known_gsm_numbers", sa.String, nullable=True),
        sa.Column("relationship", sa.String, nullable=False),
        sa.Column("occupation", sa.String, nullable=True),
        sa.Column("residential_address", sa.String, nullable=True),
        sa.Column("last_seen_date", sa.Date, nullable=True),
        sa.Column("last_seen_time", sa.Time(timezone=True), nullable=True),
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
    op.drop_table("known_associates")
