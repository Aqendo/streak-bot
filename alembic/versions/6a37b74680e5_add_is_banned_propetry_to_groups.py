"""add is_banned propetry to Groups

Revision ID: 6a37b74680e5
Revises: 
Create Date: 2023-12-08 11:47:04.175067

"""
from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "6a37b74680e5"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "groups",
        sa.Column(
            "is_banned",
            sa.Boolean,
            default=False,
            nullable=False,
            server_default=sa.text("FALSE"),
        ),
    )


def downgrade() -> None:
    op.drop_column("groups", "is_banned")
