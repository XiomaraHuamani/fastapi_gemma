"""Fix locales padre

Revision ID: 72c358381cdc
Revises: f3880afcb949
Create Date: 2025-02-06 11:38:58.898286

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '72c358381cdc'
down_revision: Union[str, None] = 'f3880afcb949'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('locales', sa.Column('subnivel_de_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'locales', 'locales', ['subnivel_de_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'locales', type_='foreignkey')
    op.drop_column('locales', 'subnivel_de_id')
    # ### end Alembic commands ###
