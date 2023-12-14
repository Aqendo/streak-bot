"""rename table

Revision ID: 499dfb1fa923
Revises: 53808d604943
Create Date: 2023-12-14 19:06:05.825696

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '499dfb1fa923'
down_revision: Union[str, None] = '53808d604943'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    op.rename_table('groups', 'group_user')
    op.execute('ALTER SEQUENCE groups_id_seq RENAME TO group_user_id_seq')
    op.execute('ALTER INDEX groups_pkey RENAME TO group_user_pkey')
    op.drop_column('group_user', 'autodelete')
    op.create_table('group',
        sa.Column('id', sa.BigInteger(), nullable=False, primary_key=True),
        sa.Column('group_id', sa.BigInteger(), nullable=False),
        sa.Column('autodelete', sa.Boolean(), nullable=False, default=False, server_default=sa.text("FALSE")),
        sa.PrimaryKeyConstraint('id'),
    )

def downgrade():
    op.rename_table('group_user', 'groups')
    op.execute('ALTER SEQUENCE group_user_id_seq RENAME TO groups_id_seq')
    op.execute('ALTER INDEX group_user_pkey RENAME TO groups_pkey')
    op.add_column('group_user', sa.Column('autodelete', sa.Boolean(), default=False, server_default=sa.text("FALSE"), nullable=False))
    op.drop_table('group')