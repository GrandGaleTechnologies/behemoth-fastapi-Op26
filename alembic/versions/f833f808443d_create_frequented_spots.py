"""
create: frequented_spots

Revision ID: f833f808443d
Revises: a6e472b32ee7
Create Date: 2024-08-25 12:47:28.598399

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f833f808443d"
down_revision: Union[str, None] = "a6e472b32ee7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "frequented_spots",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column(
            "poi_id",
            sa.Integer,
            sa.ForeignKey("pois.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("country", sa.String, nullable=False),
        sa.Column("state", sa.String, nullable=False),
        sa.Column("lga", sa.String, nullable=False),
        sa.Column("address", sa.String, nullable=False),
        sa.Column("from_date", sa.Date, nullable=True),
        sa.Column("to_date", sa.Date, nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
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
    op.drop_table("frequented_spots")
