from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.deps import get_current_user
from app.db.session import get_db
from app.schemas.dashboard import DashboardResponse
from app.services.dashboard_service import obter_dashboard

router = APIRouter()


@router.get("/dashboard", response_model=DashboardResponse)
async def dashboard(
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    return await obter_dashboard(db)
