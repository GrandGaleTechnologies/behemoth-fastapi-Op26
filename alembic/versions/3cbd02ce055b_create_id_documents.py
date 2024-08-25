"""
create: id_documents

Revision ID: 3cbd02ce055b
Revises: 2c654ac7cb6e
Create Date: 2024-08-25 12:20:29.063658

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "3cbd02ce055b"
down_revision: Union[str, None] = "2c654ac7cb6e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "id_documents",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column(
            "poi_id",
            sa.Integer,
            sa.ForeignKey("pois.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("type", sa.String, nullable=False),
        sa.Column("id_number", sa.String, nullable=False),
        sa.Column("is_deleted", sa.String, nullable=False),
        sa.Column("edited_at", sa.String, nullable=True),
        sa.Column("created_at", sa.String, nullable=False),
        sa.Column("deleted_at", sa.String, nullable=True),
    )


def downgrade() -> None:
    op.drop_table("id_documents")
