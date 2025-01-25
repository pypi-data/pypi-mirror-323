"""Specify check method

Revision ID: dcf73fa19fce
Revises: c780864dc407
Create Date: 2024-11-26 14:40:27.510587

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "dcf73fa19fce"
down_revision: Union[str, None] = "c780864dc407"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table("tasks", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "method",
                sa.Enum(
                    "GET",
                    "HEAD",
                    "POST",
                    "OPTIONS",
                    "CONNECT",
                    "TRACE",
                    "PUT",
                    "PATCH",
                    "DELETE",
                    name="method",
                ),
                nullable=False,
                server_default="GET",
            )
        )


def downgrade() -> None:
    with op.batch_alter_table("tasks", schema=None) as batch_op:
        batch_op.drop_column("method")
