"""Método de cálculo e status de integração.

Revision ID: 005_metodo_calculo
Revises: 004_configuracao_api
"""

from alembic import op
import sqlalchemy as sa


revision = "005_metodo_calculo"
down_revision = "004_configuracao_api"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("transportadoras", sa.Column("metodo_calculo", sa.String(40), nullable=True))
    op.add_column("transportadoras", sa.Column("api_ambiente", sa.String(30), nullable=True))
    op.add_column("transportadoras", sa.Column("status_integracao", sa.String(40), nullable=True))
    op.execute("""
        UPDATE transportadoras SET metodo_calculo = CASE
            WHEN tipo_integracao = 'tabela' THEN 'tabela_propria'
            WHEN tipo_integracao = 'api' THEN 'api'
            WHEN tipo_integracao IN ('webservice', 'soap') THEN 'webservice'
            ELSE 'manual' END
    """)
    op.execute("""
        UPDATE transportadoras SET status_integracao = CASE
            WHEN tipo_integracao = 'api' THEN 'pendente_credencial'
            ELSE 'nao_aplicavel' END
    """)
    op.alter_column("transportadoras", "metodo_calculo", nullable=False, server_default="manual")
    op.alter_column("transportadoras", "status_integracao", nullable=False, server_default="nao_aplicavel")


def downgrade() -> None:
    op.drop_column("transportadoras", "status_integracao")
    op.drop_column("transportadoras", "api_ambiente")
    op.drop_column("transportadoras", "metodo_calculo")
