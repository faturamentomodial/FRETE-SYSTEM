"""Exclusão lógica de transportadoras.

Revision ID: 006_soft_delete
Revises: 005_metodo_calculo
"""

from alembic import op
import sqlalchemy as sa


revision = "006_soft_delete"
down_revision = "005_metodo_calculo"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("transportadoras", sa.Column("deleted_at", sa.DateTime(), nullable=True))
    op.create_index("ix_transportadoras_deleted_at", "transportadoras", ["deleted_at"])


def downgrade() -> None:
    op.drop_index("ix_transportadoras_deleted_at", table_name="transportadoras")
    op.drop_column("transportadoras", "deleted_at")
