"""
create: educational_backgrounds

Revision ID: 994e5518c90e
Revises: 4a6509a7157e
Create Date: 2024-08-25 12:41:03.077610

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "994e5518c90e"
down_revision: Union[str, None] = "4a6509a7157e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "educational_backgrounds",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column(
            "poi_id",
            sa.Integer,
            sa.ForeignKey("pois.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("type", sa.String, nullable=False),
        sa.Column("institute_name", sa.String, nullable=False),
        sa.Column("country", sa.String, nullable=False),
        sa.Column("state", sa.String, nullable=False),
        sa.Column("current_institute", sa.String, nullable=False),
        sa.Column("from_date", sa.String, nullable=True),
        sa.Column("to_date", sa.String, nullable=True),
        sa.Column("is_deleted", sa.String, nullable=False),
        sa.Column("edited_at", sa.String, nullable=True),
        sa.Column("created_at", sa.String, nullable=False),
        sa.Column("deleted_at", sa.String, nullable=True),
    )


def downgrade() -> None:
    op.drop_table("educational_backgrounds")
