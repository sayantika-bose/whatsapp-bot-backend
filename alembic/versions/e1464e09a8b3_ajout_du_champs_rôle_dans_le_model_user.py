"""ajout du champs rôle dans le model user

Revision ID: e1464e09a8b3
Revises: 
Create Date: 2025-07-04 00:26:37.463617

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e1464e09a8b3'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('financial_advisors', sa.Column('role', sa.Enum('ADMIN', 'DEV', name='userroleenum'), nullable=False, server_default='DEV'))


def downgrade() -> None:
    op.drop_column('financial_advisors', 'role', server_default=None)
    # ### end Alembic commands ###
