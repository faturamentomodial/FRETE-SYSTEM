"""Integração de cotação Sankhya.

Revision ID: 008_integracao_sankhya
Revises: 007_configuracoes_sistema
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "008_integracao_sankhya"
down_revision = "007_configuracoes_sistema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "sankhya_transportadoras_mapeamentos",
        sa.Column("id", postgresql.UUID(as_uuid=False), primary_key=True),
        sa.Column("transportadora_id", postgresql.UUID(as_uuid=False), sa.ForeignKey("transportadoras.id", ondelete="CASCADE"), nullable=False),
        sa.Column("codigo_parceiro", sa.Integer(), nullable=False),
        sa.Column("nome_parceiro", sa.String(255), nullable=False),
        sa.Column("codigo_servico", sa.String(100), nullable=True),
        sa.Column("servico", sa.String(120), nullable=True),
        sa.Column("ativo", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("transportadora_id"),
        sa.UniqueConstraint("codigo_parceiro"),
    )
    op.create_index("ix_sankhya_transportadoras_mapeamentos_transportadora_id", "sankhya_transportadoras_mapeamentos", ["transportadora_id"])
    op.create_index("ix_sankhya_transportadoras_mapeamentos_codigo_parceiro", "sankhya_transportadoras_mapeamentos", ["codigo_parceiro"])


def downgrade() -> None:
    op.drop_index("ix_sankhya_transportadoras_mapeamentos_codigo_parceiro", table_name="sankhya_transportadoras_mapeamentos")
    op.drop_index("ix_sankhya_transportadoras_mapeamentos_transportadora_id", table_name="sankhya_transportadoras_mapeamentos")
    op.drop_table("sankhya_transportadoras_mapeamentos")
