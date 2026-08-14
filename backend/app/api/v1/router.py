from fastapi import APIRouter

from app.api.v1.endpoints import auth, configuracoes, cotacoes, dashboard, health, sankhya, transportadoras, tabelas_frete

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(dashboard.router, tags=["dashboard"])
api_router.include_router(transportadoras.router, tags=["transportadoras"])
api_router.include_router(tabelas_frete.router, tags=["tabelas-frete"])
api_router.include_router(cotacoes.router, tags=["cotacoes"])
api_router.include_router(configuracoes.router)
api_router.include_router(sankhya.router)
