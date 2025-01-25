"""Add request data to tasks

Revision ID: 31255a412d63
Revises: 80a29f64f91c
Create Date: 2024-12-09 16:40:20.926138

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "31255a412d63"
down_revision: Union[str, None] = "80a29f64f91c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("tasks", schema=None) as batch_op:
        batch_op.add_column(sa.Column("request_data", sa.String(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("tasks", schema=None) as batch_op:
        batch_op.drop_column("request_data")
