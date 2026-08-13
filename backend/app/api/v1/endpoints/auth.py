from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.deps import get_current_user
from app.core.security import create_access_token, verify_password
from app.db.session import get_db
from app.models.models import Role, SystemSetting, User
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.configuracoes import CurrentUserOut, RoleOut

router = APIRouter()


@router.post("/auth/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == payload.email).options(selectinload(User.roles).selectinload(Role.permissions)))
    user = result.scalar_one_or_none()

    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciais inválidas.")
    if not user.ativa:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Usuário desativado.")

    user.last_login_at = datetime.utcnow()
    await db.commit()
    sessao = await db.scalar(select(SystemSetting).where(SystemSetting.categoria == "seguranca", SystemSetting.chave == "sessao"))
    expiracao = int((sessao.valor if sessao else {}).get("expiracao_token_minutos", 60))
    token = create_access_token(subject=user.id, expires_minutes=expiracao)
    return TokenResponse(access_token=token)


@router.get("/auth/me", response_model=CurrentUserOut)
async def me(user: User = Depends(get_current_user)):
    roles = [RoleOut(id=role.id, nome=role.nome, descricao=role.descricao,
        permissions=sorted(item.codigo for item in role.permissions)) for role in user.roles]
    permissions = sorted({item.codigo for role in user.roles for item in role.permissions})
    return CurrentUserOut(id=user.id, nome=user.nome, email=user.email, ativa=user.ativa,
        two_factor_enabled=user.two_factor_enabled, last_login_at=user.last_login_at,
        created_at=user.created_at, roles=roles, permissions=permissions)
