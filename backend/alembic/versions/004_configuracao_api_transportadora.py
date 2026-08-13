"""Configuração genérica de API por transportadora.

Revision ID: 004_configuracao_api
Revises: 003_dados_importados_excel
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "004_configuracao_api"
down_revision = "003_dados_importados_excel"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "transportadoras_configuracoes_api",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("transportadora_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("base_url", sa.String(500), nullable=False),
        sa.Column("endpoint_cotacao", sa.String(500), nullable=False),
        sa.Column("metodo_http", sa.String(10), nullable=False),
        sa.Column("tipo_autenticacao", sa.String(30), nullable=False),
        sa.Column("nome_header", sa.String(120), nullable=True),
        sa.Column("credencial_criptografada", sa.Text(), nullable=True),
        sa.Column("campo_valor", sa.String(200), nullable=False),
        sa.Column("campo_prazo", sa.String(200), nullable=False),
        sa.Column("ativa", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["transportadora_id"], ["transportadoras.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("transportadora_id"),
    )
    op.create_index("ix_configuracao_api_transportadora", "transportadoras_configuracoes_api", ["transportadora_id"], unique=True)


def downgrade() -> None:
    op.drop_table("transportadoras_configuracoes_api")
