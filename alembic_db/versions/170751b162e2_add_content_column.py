"""add content column

Revision ID: 170751b162e2
Revises: 510cb95b6d23
Create Date: 2024-06-10 16:33:14.653625

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '170751b162e2'
down_revision: Union[str, None] = '510cb95b6d23'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('posts',sa.Column('content',sa.String(),nullable=False))
    pass


def downgrade() -> None:
    op.drop_column('posts','content')
    pass
