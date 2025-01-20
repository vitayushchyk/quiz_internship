"""upd_invite_table

Revision ID: 8a5730d3778f
Revises: 7a3c9436da2c
Create Date: 2025-01-17 13:15:18.895176

"""

from typing import Sequence, Union

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "8a5730d3778f"
down_revision: Union[str, None] = "7a3c9436da2c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    op.create_table(
        "invites",
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
            "invite_status",
            postgresql.ENUM("ACCEPTED", "REJECTED", "PENDING", name="invite_status"),
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
    op.drop_table("company_membership")


def downgrade() -> None:

    op.create_table(
        "company_membership",
        sa.Column("id", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column("company_id", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column("user_id", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "membership_status",
            postgresql.ENUM(
                "ACCEPTED", "REJECTED", "PENDING", name="membership_status"
            ),
            autoincrement=False,
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["company_id"], ["companies.id"], name="company_membership_company_id_fkey"
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name="company_membership_user_id_fkey"
        ),
        sa.PrimaryKeyConstraint("id", name="company_membership_pkey"),
    )
    op.drop_table("invites")
