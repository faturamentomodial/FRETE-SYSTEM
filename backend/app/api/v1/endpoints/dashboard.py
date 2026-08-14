from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import require_permission
from app.db.session import get_db
from app.schemas.dashboard import DashboardResponse
from app.services.dashboard_service import obter_dashboard

router = APIRouter()


@router.get("/dashboard", response_model=DashboardResponse)
async def dashboard(
    db: AsyncSession = Depends(get_db),
    _user=Depends(require_permission("cotacoes.view")),
):
    return await obter_dashboard(db)
