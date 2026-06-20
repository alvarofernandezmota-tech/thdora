"""
Sprint 5 — Añadir user_id a todos los modelos + tabla allowed_users.

Revision ID: sprint5_user_id
Create Date: 2026-06-17

⚠️  ANTES DE EJECUTAR EN MADRE:
    1. Corre: alembic history
    2. Copia el último revision ID
    3. Pégalo en down_revision abajo
    4. Luego: alembic upgrade head
"""
from alembic import op
import sqlalchemy as sa

revision = "sprint5_user_id"
down_revision = "001_add_user_id"  # ⚠️ AJUSTAR con: alembic history
branch_labels = None
depends_on = None


def upgrade() -> None:
    # appointments
    with op.batch_alter_table("appointments") as batch_op:
        batch_op.add_column(sa.Column("user_id", sa.Integer(), nullable=False, server_default="0"))
        batch_op.create_index("ix_appointments_user_id", ["user_id"])

    # habits
    with op.batch_alter_table("habits") as batch_op:
        batch_op.add_column(sa.Column("user_id", sa.Integer(), nullable=False, server_default="0"))
        batch_op.create_index("ix_habits_user_id", ["user_id"])

    # habit_config
    with op.batch_alter_table("habit_config") as batch_op:
        batch_op.add_column(sa.Column("user_id", sa.Integer(), nullable=False, server_default="0"))
        batch_op.create_index("ix_habit_config_user_id", ["user_id"])

    # allowed_users (nueva tabla)
    op.create_table(
        "allowed_users",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), nullable=False, unique=True),
        sa.Column("username", sa.String(100), nullable=True),
        sa.Column("added_at", sa.String(30), nullable=False),
        sa.Column("added_by", sa.Integer(), nullable=True),
    )
    op.create_index("ix_allowed_users_user_id", "allowed_users", ["user_id"], unique=True)


def downgrade() -> None:
    op.drop_table("allowed_users")
    with op.batch_alter_table("habit_config") as batch_op:
        batch_op.drop_index("ix_habit_config_user_id")
        batch_op.drop_column("user_id")
    with op.batch_alter_table("habits") as batch_op:
        batch_op.drop_index("ix_habits_user_id")
        batch_op.drop_column("user_id")
    with op.batch_alter_table("appointments") as batch_op:
        batch_op.drop_index("ix_appointments_user_id")
        batch_op.drop_column("user_id")
