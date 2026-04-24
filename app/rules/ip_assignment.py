from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.core.enums import IPAddressStatus
from app.models.intake import IntakeRequest
from app.models.ipam import IPAddress, Subnet


@dataclass
class RuleEvaluationResult:
    outcome: str
    summary: str
    recommended_ip: IPAddress | None = None


class IPAssignmentRuleEngine:
    def __init__(self, db: Session):
        self.db = db

    def evaluate_request(self, request: IntakeRequest) -> RuleEvaluationResult:
        subnet = self._resolve_subnet(request)
        if not subnet:
            return RuleEvaluationResult(
                outcome="review_needed",
                summary="No matching subnet could be resolved from the request.",
            )

        ips = (
            self.db.query(IPAddress)
            .filter(IPAddress.subnet_id == subnet.id)
            .order_by(IPAddress.address.asc())
            .all()
        )
        if not ips:
            return RuleEvaluationResult(
                outcome="review_needed",
                summary=f"Subnet {subnet.cidr} has no imported IP data to evaluate.",
            )

        candidate = None
        review_seen = False
        blocked_reasons: list[str] = []

        for ip in ips:
            if ip.status == IPAddressStatus.DHCP_POOL:
                blocked_reasons.append(f"{ip.address} is marked as DHCP pool")
                continue
            if ip.status == IPAddressStatus.ALLOCATED_CONFIRMED:
                blocked_reasons.append(f"{ip.address} is already allocated")
                continue
            if ip.status == IPAddressStatus.CONFLICT_SUSPECTED:
                review_seen = True
                continue
            if ip.status == IPAddressStatus.AVAILABLE_CANDIDATE and candidate is None:
                candidate = ip

        if candidate:
            return RuleEvaluationResult(
                outcome="candidate",
                summary=f"{candidate.address} is the best deterministic candidate in subnet {subnet.cidr}.",
                recommended_ip=candidate,
            )
        if review_seen:
            return RuleEvaluationResult(
                outcome="review_needed",
                summary=f"Manual review required in subnet {subnet.cidr} because conflict-suspected evidence exists and no clean candidate was selected.",
            )
        return RuleEvaluationResult(
            outcome="blocked",
            summary="; ".join(blocked_reasons) or "All known IPs are blocked by deterministic rules.",
        )

    def _resolve_subnet(self, request: IntakeRequest) -> Subnet | None:
        if request.subnet_id:
            return self.db.query(Subnet).filter(Subnet.id == request.subnet_id).first()
        if request.vlan_or_subnet:
            return self.db.query(Subnet).filter(Subnet.cidr == request.vlan_or_subnet).first()
        return None
