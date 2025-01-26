"""Use bigint for results id field

Revision ID: bd4b4962696a
Revises: 31255a412d63
Create Date: 2025-01-06 11:44:37.552965

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "bd4b4962696a"
down_revision: Union[str, None] = "31255a412d63"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    if bind.engine.name != "sqlite":
        with op.batch_alter_table("results", schema=None) as batch_op:
            batch_op.alter_column(
                "id",
                existing_type=sa.INTEGER(),
                type_=sa.BigInteger(),
                existing_nullable=False,
            )


def downgrade() -> None:
    bind = op.get_bind()
    if bind.engine.name != "sqlite":
        with op.batch_alter_table("results", schema=None) as batch_op:
            batch_op.alter_column(
                "id",
                existing_type=sa.BigInteger(),
                type_=sa.INTEGER(),
                existing_nullable=False,
            )
