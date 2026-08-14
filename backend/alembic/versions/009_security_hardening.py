"""Security hardening: revocable sessions.

Revision ID: 009_security_hardening
Revises: 008_integracao_sankhya
"""

from alembic import op
import sqlalchemy as sa

revision = "009_security_hardening"
down_revision = "008_integracao_sankhya"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("session_version", sa.Integer(), nullable=False, server_default="0"))


def downgrade() -> None:
    op.drop_column("users", "session_version")
