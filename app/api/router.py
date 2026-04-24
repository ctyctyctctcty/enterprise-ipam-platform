from fastapi import APIRouter

from app.api.routers import ai, audit, auth, dashboard, health, imports, intake, ipam, topology, workflow

api_router = APIRouter()
api_router.include_router(health.router, tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(ipam.router, prefix="/ipam", tags=["ipam"])
api_router.include_router(intake.router, prefix="/requests", tags=["intake"])
api_router.include_router(imports.router, prefix="/imports", tags=["imports"])
api_router.include_router(workflow.router, prefix="/workflow", tags=["workflow"])
api_router.include_router(audit.router, prefix="/audit", tags=["audit"])
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])
api_router.include_router(topology.router, prefix="/topology", tags=["topology"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
