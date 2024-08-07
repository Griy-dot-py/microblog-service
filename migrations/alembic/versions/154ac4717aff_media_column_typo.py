"""Media column typo

Revision ID: 154ac4717aff
Revises: 09589b667c08
Create Date: 2024-08-05 13:20:22.451219

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '154ac4717aff'
down_revision: Union[str, None] = '09589b667c08'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('media', sa.Column('author_id', sa.Integer(), nullable=False))
    op.drop_constraint('media_auhor_id_fkey', 'media', type_='foreignkey')
    op.create_foreign_key(None, 'media', 'user', ['author_id'], ['id'])
    op.drop_column('media', 'auhor_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('media', sa.Column('auhor_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'media', type_='foreignkey')
    op.create_foreign_key('media_auhor_id_fkey', 'media', 'user', ['auhor_id'], ['id'])
    op.drop_column('media', 'author_id')
    # ### end Alembic commands ###
