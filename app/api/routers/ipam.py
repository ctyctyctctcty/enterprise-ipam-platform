from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.core.enums import IPAddressStatus
from app.schemas.ipam import (
    ConflictSummary,
    IPAddressCreate,
    IPAddressDetailRead,
    IPAddressListFilter,
    IPAddressLookupResult,
    IPAddressRead,
    OutletMappingRead,
    SubnetUsageRead,
)
from app.services.ipam import IPAMService

router = APIRouter()


@router.get("/ips", response_model=list[IPAddressRead])
def list_ips(
    status: IPAddressStatus | None = None,
    subnet_id: str | None = None,
    address_contains: str | None = None,
    db: Session = Depends(get_db),
) -> list[IPAddressRead]:
    filters = IPAddressListFilter(
        status=status,
        subnet_id=subnet_id,
        address_contains=address_contains,
    )
    return IPAMService(db).list_ips(filters)


@router.post("/ips", response_model=IPAddressRead)
def create_ip(payload: IPAddressCreate, db: Session = Depends(get_db)) -> IPAddressRead:
    return IPAMService(db).create_ip(payload)


@router.get("/ips/{ip_id}", response_model=IPAddressDetailRead)
def get_ip(ip_id: str, db: Session = Depends(get_db)) -> IPAddressDetailRead:
    ip = IPAMService(db).get_ip(ip_id)
    if not ip:
        raise HTTPException(status_code=404, detail="IP not found")
    return ip


@router.get("/lookup", response_model=IPAddressLookupResult)
def lookup_ip(address: str = Query(...), db: Session = Depends(get_db)) -> IPAddressLookupResult:
    ip = IPAMService(db).get_by_address(address)
    return IPAddressLookupResult(found=ip is not None, ip=ip)


@router.get("/conflicts", response_model=list[ConflictSummary])
def list_conflicts(db: Session = Depends(get_db)) -> list[ConflictSummary]:
    return IPAMService(db).list_conflicts()


@router.get("/subnets/{subnet_id}/usage", response_model=SubnetUsageRead)
def subnet_usage(subnet_id: str, db: Session = Depends(get_db)) -> SubnetUsageRead:
    usage = IPAMService(db).subnet_usage(subnet_id)
    if not usage:
        raise HTTPException(status_code=404, detail="Subnet not found")
    return usage


@router.get("/outlet-mappings", response_model=list[OutletMappingRead])
def outlet_mappings(db: Session = Depends(get_db)) -> list[OutletMappingRead]:
    return IPAMService(db).outlet_port_mapping()
