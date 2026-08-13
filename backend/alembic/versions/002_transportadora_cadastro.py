"""Adicionar dados cadastrais de transportadoras.

Revision ID: 002_transportadora_cadastro
Revises: 001_initial_tabela_frete
"""

from alembic import op
import sqlalchemy as sa


revision = "002_transportadora_cadastro"
down_revision = "001_initial_tabela_frete"
branch_labels = None
depends_on = None


def _cpf(numero: int) -> str:
    base = f"{numero:09d}"[-9:]
    primeiro = (sum(int(digito) * peso for digito, peso in zip(base, range(10, 1, -1))) * 10) % 11
    primeiro = 0 if primeiro == 10 else primeiro
    parcial = f"{base}{primeiro}"
    segundo = (sum(int(digito) * peso for digito, peso in zip(parcial, range(11, 1, -1))) * 10) % 11
    segundo = 0 if segundo == 10 else segundo
    return f"{parcial}{segundo}"


def upgrade() -> None:
    op.add_column("transportadoras", sa.Column("razao_social", sa.String(255), nullable=True))
    op.add_column("transportadoras", sa.Column("cnpj_cpf", sa.String(14), nullable=True))
    op.add_column("transportadoras", sa.Column("segmento", sa.String(80), nullable=True))

    conexao = op.get_bind()
    registros = conexao.execute(sa.text("SELECT id, nome FROM transportadoras ORDER BY nome")).mappings().all()
    for indice, registro in enumerate(registros, start=1):
        conexao.execute(
            sa.text(
                "UPDATE transportadoras SET razao_social=:razao, cnpj_cpf=:documento, "
                "segmento='rodoviario' WHERE id=:id"
            ),
            {"razao": f"{registro['nome']} Transportes Ltda.", "documento": _cpf(100_000_000 + indice), "id": registro["id"]},
        )

    op.alter_column("transportadoras", "razao_social", nullable=False)
    op.alter_column("transportadoras", "cnpj_cpf", nullable=False)
    op.alter_column("transportadoras", "segmento", nullable=False)
    op.create_index("ix_transportadoras_cnpj_cpf", "transportadoras", ["cnpj_cpf"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_transportadoras_cnpj_cpf", table_name="transportadoras")
    op.drop_column("transportadoras", "segmento")
    op.drop_column("transportadoras", "cnpj_cpf")
    op.drop_column("transportadoras", "razao_social")
