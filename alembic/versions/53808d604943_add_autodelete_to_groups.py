"""add autodelete to groups

Revision ID: 53808d604943
Revises: 6a37b74680e5
Create Date: 2023-12-14 15:39:41.554598

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '53808d604943'
down_revision: Union[str, None] = '6a37b74680e5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("groups", sa.Column("autodelete", sa.Boolean, default=False, nullable=False, server_default=sa.text("FALSE")))


def downgrade() -> None:
    op.drop_column("groups", "autodelete")