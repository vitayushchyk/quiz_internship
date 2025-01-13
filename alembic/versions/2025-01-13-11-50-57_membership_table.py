"""membership_table

Revision ID: 564dfda4f527
Revises: 449e7a485adf
Create Date: 2025-01-13 11:50:57.149200

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "564dfda4f527"
down_revision: Union[str, None] = "449e7a485adf"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.create_table(
        "company_membership",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("company_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "membership_status",
            postgresql.ENUM(
                "INVITATION_PENDING",
                "REQUEST_PENDING",
                "ACTIVE_MEMBER",
                "INVITATION_REJECTED",
                "REQUEST_REJECTED",
                name="membership_status",
            ),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["company_id"],
            ["companies.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:

    op.drop_table("company_membership")
