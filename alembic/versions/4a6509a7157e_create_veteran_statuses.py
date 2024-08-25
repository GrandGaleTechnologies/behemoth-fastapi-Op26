"""
create: veteran_statuses

Revision ID: 4a6509a7157e
Revises: 569c7b3bbe01
Create Date: 2024-08-25 12:36:46.534167

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "4a6509a7157e"
down_revision: Union[str, None] = "569c7b3bbe01"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "veteran_statuses",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column(
            "poi_id",
            sa.Integer,
            sa.ForeignKey("pois.id", ondelete="CASCADE"),
            unique=True,
            nullable=False,
        ),
        sa.Column("is_veteran", sa.String, nullable=False),
        sa.Column("section", sa.String, nullable=False),
        sa.Column("location", sa.String, nullable=False),
        sa.Column("id_card", sa.String, nullable=True),
        sa.Column("id_card_issuer", sa.String, nullable=True),
        sa.Column("from_date", sa.String, nullable=True),
        sa.Column("to_date", sa.String, nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("is_deleted", sa.String, nullable=False),
        sa.Column("edited_at", sa.String, nullable=True),
        sa.Column("created_at", sa.String, nullable=False),
        sa.Column("deleted_at", sa.String, nullable=True),
    )


def downgrade() -> None:
    op.drop_table("veteran_statuses")
