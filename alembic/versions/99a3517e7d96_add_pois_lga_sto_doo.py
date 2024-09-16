"""
add: pois-lga,sto,doo

Revision ID: 99a3517e7d96
Revises: 83846deab39f
Create Date: 2024-09-16 13:06:49.753214

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "99a3517e7d96"
down_revision: Union[str, None] = "83846deab39f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("pois", sa.Column("state_of_origin", sa.String, nullable=True))
    op.add_column("pois", sa.Column("lga_of_origin", sa.String, nullable=True))
    op.add_column("pois", sa.Column("district_of_origin", sa.String, nullable=True))


def downgrade() -> None:
    op.drop_column("pois", "state_of_origin")
    op.drop_column("pois", "lga_of_origin")
    op.drop_column("pois", "district_of_origin")
