"""
create: poi_application_processes

Revision ID: 83846deab39f
Revises: 417eb096dc40
Create Date: 2024-08-26 16:43:31.612824

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "83846deab39f"
down_revision: Union[str, None] = "417eb096dc40"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "poi_application_processes",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column(
            "poi_id",
            sa.Integer,
            sa.ForeignKey("pois.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("other_profile", sa.String, nullable=False),
        sa.Column("employment", sa.String, nullable=False),
        sa.Column("veteran_status", sa.String, nullable=False),
        sa.Column("education", sa.String, nullable=False),
        sa.Column("case_file", sa.String, nullable=False),
        sa.Column("fingerprints", sa.String, nullable=False),
    )


def downgrade() -> None:
    op.drop_table("poi_application_processes")
