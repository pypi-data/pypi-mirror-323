"""Add recheck delay

Revision ID: 127d74c770bb
Revises: dcf73fa19fce
Create Date: 2024-11-27 16:04:58.138768

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "127d74c770bb"
down_revision: Union[str, None] = "dcf73fa19fce"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("tasks", schema=None) as batch_op:
        batch_op.add_column(sa.Column("recheck_delay", sa.Float(), nullable=True))
        batch_op.add_column(
            sa.Column(
                "already_retried",
                sa.Boolean(),
                nullable=False,
                server_default=sa.sql.false(),
            )
        )


def downgrade() -> None:
    with op.batch_alter_table("tasks", schema=None) as batch_op:
        batch_op.drop_column("already_retried")
        batch_op.drop_column("recheck_delay")
