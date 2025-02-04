"""upd_quiz

Revision ID: a84438c04f44
Revises: 70276e66de98
Create Date: 2025-02-04 19:35:58.609033

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a84438c04f44"
down_revision: Union[str, None] = "70276e66de98"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column("quizzes", "created_by", existing_type=sa.INTEGER(), nullable=False)
    op.alter_column(
        "quizzes", "description", existing_type=sa.VARCHAR(length=500), nullable=False
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "quizzes", "description", existing_type=sa.VARCHAR(length=500), nullable=True
    )
    op.alter_column("quizzes", "created_by", existing_type=sa.INTEGER(), nullable=True)
    # ### end Alembic commands ###
