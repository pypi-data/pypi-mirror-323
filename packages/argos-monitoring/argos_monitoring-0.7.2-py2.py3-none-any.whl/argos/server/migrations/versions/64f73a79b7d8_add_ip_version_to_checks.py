"""Add IP version to checks

Revision ID: 64f73a79b7d8
Revises: a1e98cf72a5c
Create Date: 2024-12-02 14:12:40.558033

"""
from typing import Sequence, Union

from alembic import op
from sqlalchemy.dialects.postgresql import ENUM
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "64f73a79b7d8"
down_revision: Union[str, None] = "a1e98cf72a5c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    enum = ENUM("4", "6", name="ip_version_enum", create_type=False)
    enum.create(op.get_bind(), checkfirst=True)
    with op.batch_alter_table("tasks", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("ip_version", enum, server_default="4", nullable=False)
        )


def downgrade() -> None:
    with op.batch_alter_table("tasks", schema=None) as batch_op:
        batch_op.drop_column("ip_version")
        ENUM(name="ip_version_enum").drop(op.get_bind(), checkfirst=True)
