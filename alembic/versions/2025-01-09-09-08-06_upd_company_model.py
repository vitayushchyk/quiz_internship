"""upd_company_model

Revision ID: d8cbc377c83b
Revises: 4d50f419607b
Create Date: 2025-01-09 09:08:06.368829

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d8cbc377c83b"
down_revision: Union[str, None] = "4d50f419607b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint(None, "companies", ["name"])


def downgrade() -> None:
    op.drop_constraint(None, "companies", type_="unique")
