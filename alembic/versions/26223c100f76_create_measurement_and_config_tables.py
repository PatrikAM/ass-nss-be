"""create measurement and config tables

Revision ID: 26223c100f76
Revises: 
Create Date: 2025-04-24 10:20:33.270351

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '26223c100f76'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'config',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('interval', sa.Integer, nullable=True),
        sa.Column('frequency', sa.Float, nullable=True),
        sa.Column('rgb_camera', sa.Boolean, nullable=True),
        sa.Column('hsi_camera', sa.Boolean, nullable=True),
        sa.Column('created_at', sa.TIMESTAMP, nullable=True),
    )

    op.create_table(
        'measurement',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('snapshot_rgb_camera', sa.String, nullable=True),
        sa.Column('snapshot_hsi_camera', sa.String, nullable=True),
        sa.Column('acustic', sa.Integer, nullable=True),
        sa.Column('created_at', sa.TIMESTAMP, nullable=True),
        sa.Column('config_id', sa.Integer, sa.ForeignKey('config.id'), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('measurement')
    op.drop_table('config')
