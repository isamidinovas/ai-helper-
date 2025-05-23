"""Remove phone field from users table

Revision ID: 2692555cb419
Revises: 9efa9492dab9
Create Date: 2025-05-05 15:00:27.272532

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2692555cb419'
down_revision: Union[str, None] = '9efa9492dab9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'phone')
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('phone', sa.VARCHAR(), autoincrement=False, nullable=True))
    # ### end Alembic commands ###
