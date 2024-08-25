"""
create: employment_histories

Revision ID: 569c7b3bbe01
Revises: 0fad53da18eb
Create Date: 2024-08-25 12:33:14.109518

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "569c7b3bbe01"
down_revision: Union[str, None] = "0fad53da18eb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "employment_histories",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column(
            "poi_id",
            sa.Integer,
            sa.ForeignKey("pois.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("company", sa.String, nullable=False),
        sa.Column("employment_type", sa.String, nullable=False),
        sa.Column("from_date", sa.String, nullable=True),
        sa.Column("to_date", sa.String, nullable=True),
        sa.Column("current_job", sa.String, nullable=False),
        sa.Column("description", sa.String, nullable=True),
        sa.Column("is_deleted", sa.String, nullable=False),
        sa.Column("edited_at", sa.String, nullable=True),
        sa.Column("created_at", sa.String, nullable=False),
        sa.Column("deleted_at", sa.String, nullable=True),
    )


def downgrade() -> None:
    op.drop_table("employment_histories")
