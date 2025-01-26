"""Add task index

Revision ID: 8b58ced14d6e
Revises: 64f73a79b7d8
Create Date: 2024-12-03 16:41:44.842213

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8b58ced14d6e"
down_revision: Union[str, None] = "64f73a79b7d8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("tasks", schema=None) as batch_op:
        batch_op.add_column(sa.Column("task_group", sa.String(), nullable=True))
    with op.batch_alter_table("tasks", schema=None) as batch_op:
        batch_op.execute(
            "UPDATE tasks SET task_group = method || '-' || ip_version || '-' || url"
        )
        batch_op.alter_column("task_group", nullable=False)
        batch_op.create_index("similar_tasks", ["task_group"], unique=False)


def downgrade() -> None:
    with op.batch_alter_table("tasks", schema=None) as batch_op:
        batch_op.drop_index("similar_tasks")
        batch_op.drop_column("task_group")
