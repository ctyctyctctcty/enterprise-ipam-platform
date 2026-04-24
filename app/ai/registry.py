from app.ai.skills.check_ip_availability import handle as check_ip_availability
from app.ai.skills.explain_ip_risk import handle as explain_ip_risk
from app.ai.skills.explain_request_risk import handle as explain_request_risk
from app.ai.skills.find_available_ips import handle as find_available_ips

SKILL_REGISTRY = {
    "check_ip_availability": check_ip_availability,
    "find_available_ips": find_available_ips,
    "explain_ip_risk": explain_ip_risk,
    "explain_request_risk": explain_request_risk,
}

