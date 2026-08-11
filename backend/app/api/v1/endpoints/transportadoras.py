from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db
from app.models.models import Transportadora
from app.schemas.auth import TransportadoraOut

router = APIRouter()


@router.get("/transportadoras", response_model=list[TransportadoraOut])
async def listar_transportadoras(
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    result = await db.execute(select(Transportadora).order_by(Transportadora.nome))
    return result.scalars().all()
