from contextlib import asynccontextmanager

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.admin.setup import setup_admin
from app.api.router import api_router
from app.core.config import settings
from app.core.db import SessionLocal
from app.models.ipam import Floor, Site
from app.services.dashboard import DashboardService


@asynccontextmanager
async def lifespan(application: FastAPI):
    yield


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Local-first enterprise internal IP management platform skeleton",
    lifespan=lifespan,
)

app.include_router(api_router, prefix="/api/v1")
setup_admin(app)
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parents[1] / "templates"))


@app.get("/", tags=["root"])
def root() -> RedirectResponse:
    return RedirectResponse(url="/dashboard", status_code=302)


@app.get("/dashboard", response_class=HTMLResponse, tags=["internal"])
def dashboard_page(request: Request, site_id: str | None = None):
    db = SessionLocal()
    try:
        dashboard_service = DashboardService(db)
        sites = db.query(Site).order_by(Site.name.asc()).all()
        return templates.TemplateResponse(
            request,
            "dashboard.html",
            {
                "sites": sites,
                "current_site_id": site_id,
                "summary": dashboard_service.summary(site_id),
                "fixed_ip_alerts": dashboard_service.fixed_ip_alerts(site_id),
                "dhcp_alerts": dashboard_service.dhcp_alerts(site_id),
                "recent_activity": dashboard_service.recent_activity(site_id),
                "page_title": "Operations Dashboard",
            },
        )
    finally:
        db.close()


@app.get("/topology", response_class=HTMLResponse, tags=["internal"])
def topology_page(request: Request):
    db = SessionLocal()
    try:
        sites = db.query(Site).order_by(Site.name.asc()).all()
        floors = db.query(Floor).order_by(Floor.floor_number.asc(), Floor.code.asc()).all()
        return templates.TemplateResponse(
            request,
            "topology.html",
            {
                "sites": sites,
                "floors": floors,
                "page_title": "Network Topology",
            },
        )
    finally:
        db.close()
