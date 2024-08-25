"""
create: fingerprints

Revision ID: a376e786c170
Revises: f833f808443d
Create Date: 2024-08-25 12:51:04.200635

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a376e786c170"
down_revision: Union[str, None] = "f833f808443d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "fingerprints",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column(
            "poi_id",
            sa.Integer,
            sa.ForeignKey("pois.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("left_thumb", sa.String, nullable=False),
        sa.Column("right_thumb", sa.String, nullable=False),
        sa.Column("left_pointer", sa.String, nullable=False),
        sa.Column("right_pointer", sa.String, nullable=False),
        sa.Column("is_deleted", sa.String, nullable=False),
        sa.Column("edited_at", sa.String, nullable=True),
        sa.Column("created_at", sa.String, nullable=False),
        sa.Column("deleted_at", sa.String, nullable=True),
    )


def downgrade() -> None:
    op.drop_table("fingerprints")
