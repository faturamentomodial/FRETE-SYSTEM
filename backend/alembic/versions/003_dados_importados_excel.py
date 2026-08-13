"""Armazenar dados estruturados de planilhas complexas.

Revision ID: 003_dados_importados_excel
Revises: 002_transportadora_cadastro
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "003_dados_importados_excel"
down_revision = "002_transportadora_cadastro"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tabelas_frete_dados_importados",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("tabela_frete_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("formato", sa.String(80), nullable=False),
        sa.Column("dados", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("quantidade_coberturas", sa.Integer(), nullable=False),
        sa.Column("quantidade_tarifas", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["tabela_frete_id"], ["tabelas_frete.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tabela_frete_id"),
    )
    op.create_index("ix_dados_importados_tabela", "tabelas_frete_dados_importados", ["tabela_frete_id"], unique=True)
    op.create_index("ix_dados_importados_formato", "tabelas_frete_dados_importados", ["formato"])


def downgrade() -> None:
    op.drop_table("tabelas_frete_dados_importados")
