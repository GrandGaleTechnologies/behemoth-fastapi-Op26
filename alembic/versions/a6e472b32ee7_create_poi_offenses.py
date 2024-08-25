"""
create: poi_offenses

Revision ID: a6e472b32ee7
Revises: 994e5518c90e
Create Date: 2024-08-25 12:44:43.637078

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a6e472b32ee7"
down_revision: Union[str, None] = "994e5518c90e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "poi_offenses",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column(
            "poi_id",
            sa.Integer,
            sa.ForeignKey("pois.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "offense_id",
            sa.Integer,
            sa.ForeignKey("offenses.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("case_id", sa.String, nullable=True),
        sa.Column("date_convicted", sa.String, nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("is_deleted", sa.String, nullable=False),
        sa.Column("edited_at", sa.String, nullable=True),
        sa.Column("created_at", sa.String, nullable=False),
        sa.Column("deleted_at", sa.String, nullable=True),
    )


def downgrade() -> None:
    op.drop_table("poi_offenses")
