"""
edit: nullable

Revision ID: f8fb5e7cf602
Revises: 417eb096dc40
Create Date: 2024-09-22 13:48:59.176936

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f8fb5e7cf602"
down_revision: Union[str, None] = "417eb096dc40"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("veteran_statuses", "section", nullable=True)
    op.alter_column("veteran_statuses", "location", nullable=True)


def downgrade() -> None:
    op.alter_column("veteran_statuses", "section", nullable=False)
    op.alter_column("veteran_statuses", "location", nullable=False)
