"""
create: pois

Revision ID: 2c654ac7cb6e
Revises: 062c0e31800d
Create Date: 2024-08-24 21:28:31.435241

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2c654ac7cb6e"
down_revision: Union[str, None] = "45b3a8e77cd7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "pois",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("pfp_url", sa.String, nullable=True),
        sa.Column("full_name", sa.String, nullable=False),
        sa.Column("alias", sa.String, nullable=False),
        sa.Column("dob", sa.String, nullable=True),
        sa.Column("pob", sa.String, nullable=True),
        sa.Column("nationality", sa.String, nullable=True),
        sa.Column("religion", sa.String, nullable=True),
        sa.Column("political_affiliation", sa.String, nullable=True),
        sa.Column("tribal_union", sa.String, nullable=True),
        sa.Column("last_seen_date", sa.String, nullable=True),
        sa.Column("last_seen_time", sa.String, nullable=True),
        sa.Column("notes", sa.Text, nullable=True),
        sa.Column("is_completed", sa.String, nullable=False),
        sa.Column("is_pinned", sa.String, nullable=False),
        sa.Column("is_deleted", sa.String, nullable=False),
        sa.Column("edited_at", sa.String, nullable=True),
        sa.Column("created_at", sa.String, nullable=False),
        sa.Column("deleted_at", sa.String, nullable=True),
    )


def downgrade() -> None:
    op.drop_table("pois")
