"""Make frequency a float

Revision ID: a1e98cf72a5c
Revises: 127d74c770bb
Create Date: 2024-11-27 16:10:13.000705

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a1e98cf72a5c"
down_revision: Union[str, None] = "127d74c770bb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("tasks", schema=None) as batch_op:
        batch_op.alter_column(
            "frequency",
            existing_type=sa.INTEGER(),
            type_=sa.Float(),
            existing_nullable=False,
        )


def downgrade() -> None:
    with op.batch_alter_table("tasks", schema=None) as batch_op:
        batch_op.alter_column(
            "frequency",
            existing_type=sa.Float(),
            type_=sa.INTEGER(),
            existing_nullable=False,
        )
