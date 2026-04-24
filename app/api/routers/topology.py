from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.schemas.topology import TopologyGraphResponse
from app.services.topology import TopologyService

router = APIRouter()


@router.get("/graph", response_model=TopologyGraphResponse)
def get_topology_graph(
    site_id: str | None = None,
    floor_id: str | None = None,
    include_ip_overlay: bool = False,
    db: Session = Depends(get_db),
) -> TopologyGraphResponse:
    return TopologyService(db).build_graph(
        site_id=site_id,
        floor_id=floor_id,
        include_ip_overlay=include_ip_overlay,
    )

