"""
create: audit_logs

Revision ID: 417eb096dc40
Revises: a376e786c170
Create Date: 2024-08-25 17:30:02.660419

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "417eb096dc40"
down_revision: Union[str, None] = "a376e786c170"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column(
            "user_id",
            sa.Integer,
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("resource", sa.String, nullable=False),
        sa.Column("action", sa.String, nullable=False),
        sa.Column("notes", sa.String, nullable=True),
        sa.Column("created_at", sa.String, nullable=False),
    )


def downgrade() -> None:
    op.drop_table("audit_logs")
