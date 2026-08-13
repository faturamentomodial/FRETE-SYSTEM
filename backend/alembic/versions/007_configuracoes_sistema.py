"""Modelos base da tela de configurações.

Revision ID: 007_configuracoes_sistema
Revises: 006_soft_delete
"""

from __future__ import annotations

import json
import uuid

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "007_configuracoes_sistema"
down_revision = "006_soft_delete"
branch_labels = None
depends_on = None


PERMISSOES = {
    "settings.view": "Visualizar configurações do sistema",
    "settings.manage": "Alterar configurações do sistema",
    "users.view": "Visualizar usuários e perfis",
    "users.manage": "Criar, editar e desativar usuários",
    "integrations.view": "Visualizar integrações globais",
    "integrations.manage": "Configurar integrações globais e credenciais",
    "audit.view": "Visualizar logs de auditoria",
    "cotacoes.view": "Visualizar cotações",
    "cotacoes.manage": "Criar e alterar cotações",
    "transportadoras.view": "Visualizar transportadoras e tabelas",
    "transportadoras.manage": "Gerenciar transportadoras e tabelas",
}


def _id() -> str:
    return str(uuid.uuid4())


def upgrade() -> None:
    op.add_column("users", sa.Column("ativa", sa.Boolean(), nullable=False, server_default=sa.true()))
    op.add_column("users", sa.Column("two_factor_enabled", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.add_column("users", sa.Column("two_factor_secret_encrypted", sa.Text(), nullable=True))
    op.add_column("users", sa.Column("last_login_at", sa.DateTime(), nullable=True))
    op.add_column("users", sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")))
    op.create_index("ix_users_ativa", "users", ["ativa"])

    op.create_table(
        "roles",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("nome", sa.String(50), nullable=False),
        sa.Column("descricao", sa.String(255), nullable=True),
        sa.Column("sistema", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_roles_nome", "roles", ["nome"], unique=True)

    op.create_table(
        "permissions",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("codigo", sa.String(100), nullable=False),
        sa.Column("descricao", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_permissions_codigo", "permissions", ["codigo"], unique=True)

    op.create_table(
        "user_roles",
        sa.Column("user_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("role_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("user_id", "role_id"),
    )
    op.create_table(
        "role_permissions",
        sa.Column("role_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("permission_id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["permission_id"], ["permissions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("role_id", "permission_id"),
    )

    op.create_table(
        "system_settings",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("categoria", sa.String(50), nullable=False),
        sa.Column("chave", sa.String(100), nullable=False),
        sa.Column("valor", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("descricao", sa.String(255), nullable=True),
        sa.Column("updated_by_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["updated_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("categoria", "chave", name="uq_system_settings_categoria_chave"),
    )
    op.create_index("ix_system_settings_categoria", "system_settings", ["categoria"])

    op.create_table(
        "integration_credentials",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("codigo", sa.String(80), nullable=False),
        sa.Column("nome", sa.String(120), nullable=False),
        sa.Column("tipo", sa.String(50), nullable=False),
        sa.Column("configuracao", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("credenciais_criptografadas", sa.Text(), nullable=True),
        sa.Column("status", sa.String(30), nullable=False, server_default="pendente"),
        sa.Column("ultimo_erro", sa.Text(), nullable=True),
        sa.Column("ultima_verificacao_at", sa.DateTime(), nullable=True),
        sa.Column("ativa", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("updated_by_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["updated_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_integration_credentials_codigo", "integration_credentials", ["codigo"], unique=True)
    op.create_index("ix_integration_credentials_status", "integration_credentials", ["status"])

    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=False), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=False), nullable=True),
        sa.Column("acao", sa.String(80), nullable=False),
        sa.Column("recurso", sa.String(80), nullable=False),
        sa.Column("recurso_id", sa.String(100), nullable=True),
        sa.Column("dados_anteriores", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("dados_novos", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_audit_logs_user_id", "audit_logs", ["user_id"])
    op.create_index("ix_audit_logs_acao", "audit_logs", ["acao"])
    op.create_index("ix_audit_logs_recurso", "audit_logs", ["recurso"])
    op.create_index("ix_audit_logs_recurso_id", "audit_logs", ["recurso_id"])
    op.create_index("ix_audit_logs_created_at", "audit_logs", ["created_at"])

    conexao = op.get_bind()
    role_ids = {nome: _id() for nome in ("admin", "operador", "visualizacao")}
    for nome, descricao in (
        ("admin", "Acesso completo ao sistema"),
        ("operador", "Operação de cotações, transportadoras e tabelas"),
        ("visualizacao", "Acesso somente para consulta"),
    ):
        conexao.execute(sa.text(
            "INSERT INTO roles (id, nome, descricao, sistema) VALUES (:id, :nome, :descricao, true)"
        ), {"id": role_ids[nome], "nome": nome, "descricao": descricao})

    permission_ids: dict[str, str] = {}
    for codigo, descricao in PERMISSOES.items():
        permission_ids[codigo] = _id()
        conexao.execute(sa.text(
            "INSERT INTO permissions (id, codigo, descricao) VALUES (:id, :codigo, :descricao)"
        ), {"id": permission_ids[codigo], "codigo": codigo, "descricao": descricao})

    permissoes_por_role = {
        "admin": set(PERMISSOES),
        "operador": {"settings.view", "integrations.view", "cotacoes.view", "cotacoes.manage", "transportadoras.view", "transportadoras.manage"},
        "visualizacao": {"settings.view", "integrations.view", "cotacoes.view", "transportadoras.view"},
    }
    for role, codigos in permissoes_por_role.items():
        for codigo in codigos:
            conexao.execute(sa.text(
                "INSERT INTO role_permissions (role_id, permission_id) VALUES (:role_id, :permission_id)"
            ), {"role_id": role_ids[role], "permission_id": permission_ids[codigo]})
    conexao.execute(sa.text(
        "INSERT INTO user_roles (user_id, role_id) SELECT id, :role_id FROM users WHERE email = :email"
    ), {"role_id": role_ids["admin"], "email": "admin@fretesystem.com"})

    configuracoes = [
        ("empresa", "perfil", {
            "razao_social": "", "cnpj": "", "logo_path": None,
            "endereco_origem": {"cep": "", "logradouro": "", "numero": "", "complemento": "", "bairro": "", "cidade": "", "uf": ""},
        }, "Dados da empresa e origem padrão das cotações"),
        ("cotacao", "parametros", {
            "margem_padrao_percentual": 0, "regra_arredondamento": "duas_casas",
            "validade_padrao_dias": 7, "unidade_peso": "kg", "unidade_volume": "m3", "casas_decimais": 2,
        }, "Parâmetros globais usados nas cotações"),
        ("notificacoes", "eventos", {
            "cotacao_criada": {"email": False, "webhook": False},
            "cotacao_expirada": {"email": False, "webhook": False},
            "falha_integracao": {"email": False, "webhook": False},
            "destinatarios": [], "webhook_url": "",
        }, "Canais e eventos de notificação"),
        ("seguranca", "sessao", {
            "expiracao_token_minutos": 60, "two_factor_obrigatorio": False,
        }, "Política de sessão e autenticação"),
    ]
    for categoria, chave, valor, descricao in configuracoes:
        conexao.execute(sa.text(
            "INSERT INTO system_settings (id, categoria, chave, valor, descricao) "
            "VALUES (:id, :categoria, :chave, CAST(:valor AS JSONB), :descricao)"
        ), {"id": _id(), "categoria": categoria, "chave": chave, "valor": json.dumps(valor), "descricao": descricao})

    for codigo, nome, tipo in (
        ("sankhya", "Sankhya ERP", "erp"),
        ("smtp", "Servidor de e-mail", "smtp"),
        ("geocoding_cep", "Geocodificação e CEP", "geocoding"),
    ):
        conexao.execute(sa.text(
            "INSERT INTO integration_credentials (id, codigo, nome, tipo, configuracao, status, ativa) "
            "VALUES (:id, :codigo, :nome, :tipo, '{}'::jsonb, 'pendente', false)"
        ), {"id": _id(), "codigo": codigo, "nome": nome, "tipo": tipo})


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("integration_credentials")
    op.drop_table("system_settings")
    op.drop_table("role_permissions")
    op.drop_table("user_roles")
    op.drop_table("permissions")
    op.drop_table("roles")
    op.drop_index("ix_users_ativa", table_name="users")
    op.drop_column("users", "updated_at")
    op.drop_column("users", "last_login_at")
    op.drop_column("users", "two_factor_secret_encrypted")
    op.drop_column("users", "two_factor_enabled")
    op.drop_column("users", "ativa")
