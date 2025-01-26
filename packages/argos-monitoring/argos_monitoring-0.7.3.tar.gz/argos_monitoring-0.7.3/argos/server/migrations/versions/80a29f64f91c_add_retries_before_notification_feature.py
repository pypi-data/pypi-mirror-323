"""Add retries before notification feature

Revision ID: 80a29f64f91c
Revises: 8b58ced14d6e
Create Date: 2024-12-04 17:03:35.104368

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "80a29f64f91c"
down_revision: Union[str, None] = "8b58ced14d6e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("tasks", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "retry_before_notification",
                sa.Integer(),
                server_default="0",
                nullable=False,
            )
        )
        batch_op.add_column(
            sa.Column(
                "contiguous_failures", sa.Integer(), server_default="0", nullable=False
            )
        )


def downgrade() -> None:
    with op.batch_alter_table("tasks", schema=None) as batch_op:
        batch_op.drop_column("contiguous_failures")
        batch_op.drop_column("retry_before_notification")
