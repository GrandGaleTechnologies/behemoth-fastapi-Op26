"""
create: login_attempts

Revision ID: 062c0e31800d
Revises: a21caccace01
Create Date: 2024-08-24 10:53:06.635049

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "062c0e31800d"
down_revision: Union[str, None] = "a21caccace01"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "login_attempts",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("badge_num", sa.String, nullable=False),
        sa.Column("is_success", sa.Boolean, server_default=sa.false(), nullable=False),
        sa.Column(
            "attempted_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_table("login_attempts")
