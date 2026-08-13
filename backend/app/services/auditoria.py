from typing import Any

from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import AuditLog, User


async def registrar_auditoria(
    db: AsyncSession,
    usuario: User,
    request: Request,
    acao: str,
    recurso: str,
    recurso_id: str | None = None,
    anteriores: dict[str, Any] | None = None,
    novos: dict[str, Any] | None = None,
) -> None:
    encaminhado = request.headers.get("x-forwarded-for", "").split(",")[0].strip()
    ip = encaminhado or (request.client.host if request.client else None)
    db.add(AuditLog(
        user_id=usuario.id,
        acao=acao,
        recurso=recurso,
        recurso_id=recurso_id,
        dados_anteriores=anteriores,
        dados_novos=novos,
        ip_address=ip,
        user_agent=request.headers.get("user-agent", "")[:500] or None,
    ))
