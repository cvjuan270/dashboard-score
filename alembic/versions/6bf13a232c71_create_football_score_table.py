"""create football_score table

Revision ID: 6bf13a232c71
Revises: 
Create Date: 2024-08-21 23:13:22.885069

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6bf13a232c71'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('football_results',
        sa.Column('id', sa.Integer(), primary_key=True, index=True),
        sa.Column('team', sa.String(), nullable=False),
        sa.Column('score', sa.Integer(), nullable=False),
    )

def downgrade() -> None:
    op.drop_table('football_results')
