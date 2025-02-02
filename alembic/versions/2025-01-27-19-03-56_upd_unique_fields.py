"""upd_unique_fields

Revision ID: ae767585a299
Revises: e9d3ca110ea9
Create Date: 2025-01-27 19:03:56.315904

"""

from typing import Sequence, Union

from alembic import op

revision: str = "ae767585a299"
down_revision: Union[str, None] = "e9d3ca110ea9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint(
        "unique_company_user_role",
        "company_user_roles",
        ["company_id", "user_id", "role"],
    )


def downgrade() -> None:
    op.drop_constraint("unique_company_user_role", "company_user_roles", type_="unique")
