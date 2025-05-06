"""Rename interval to interval_value in config table

Revision ID: 9bbe88895bca
Revises: 26223c100f76
Create Date: 2025-05-10 14:50:05.538644

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9bbe88895bca'
down_revision: Union[str, None] = '26223c100f76'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column('config', 'interval', new_column_name='interval_value')


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column('config', 'interval_value', new_column_name='interval')
