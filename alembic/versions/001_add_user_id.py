"""Añade user_id a appointments y habits con índice compuesto.

Revision ID: 001_add_user_id
Revises:
Create Date: 2026-06-15
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "001_add_user_id"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table("appointments", schema=None) as batch_op:
        batch_op.add_column(sa.Column("user_id", sa.Integer(), nullable=False, server_default="0"))
        batch_op.create_index("ix_appointments_user_id_fecha", ["user_id", "fecha"], unique=False)

    with op.batch_alter_table("habits", schema=None) as batch_op:
        batch_op.add_column(sa.Column("user_id", sa.Integer(), nullable=False, server_default="0"))
        batch_op.create_index("ix_habits_user_id_fecha", ["user_id", "fecha"], unique=False)


def downgrade() -> None:
    with op.batch_alter_table("habits", schema=None) as batch_op:
        batch_op.drop_index("ix_habits_user_id_fecha")
        batch_op.drop_column("user_id")

    with op.batch_alter_table("appointments", schema=None) as batch_op:
        batch_op.drop_index("ix_appointments_user_id_fecha")
        batch_op.drop_column("user_id")
