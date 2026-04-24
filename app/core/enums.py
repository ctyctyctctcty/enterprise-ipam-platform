from enum import StrEnum


class IPAddressStatus(StrEnum):
    ALLOCATED_CONFIRMED = "allocated_confirmed"
    ALLOCATED_UNVERIFIED = "allocated_unverified"
    AVAILABLE_CANDIDATE = "available_candidate"
    CONFLICT_SUSPECTED = "conflict_suspected"
    RESERVED = "reserved"
    DHCP_POOL = "dhcp_pool"


class RequestStatus(StrEnum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    ASSIGNED = "assigned"
    CLOSED = "closed"


class SourceType(StrEnum):
    EXCEL = "excel"
    DHCP = "dhcp"
    DNS = "dns"
    ARP = "arp"
    MANUAL = "manual"
    POWER_APPS = "power_apps"
    POWER_AUTOMATE = "power_automate"
    API = "api"
    ADMIN_UI = "admin_ui"


class ApprovalStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    SKIPPED = "skipped"


class ImportJobStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PARTIAL = "partial"


class AuditAction(StrEnum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    IMPORT = "import"
    APPROVE = "approve"
    ASSIGN = "assign"
    SUBMIT = "submit"
    TRANSITION = "transition"
