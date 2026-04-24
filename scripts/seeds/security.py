from app.core.security import get_password_hash
from app.models.auth import Permission, Role, User
from scripts.seeds import SeedContext


def seed_security(context: SeedContext) -> dict[str, User]:
    db = context.db

    permission_specs = [
        ("ip.read", "Read IP data"),
        ("ip.write", "Write IP data"),
        ("request.review", "Review intake requests"),
        ("audit.read", "Read audit logs"),
        ("import.run", "Run import jobs"),
        ("dashboard.read", "Read operational dashboard"),
    ]
    permissions_by_code: dict[str, Permission] = {}
    for code, name in permission_specs:
        permission = db.query(Permission).filter(Permission.code == code).first()
        if not permission:
            permission = Permission(code=code, name=name)
            db.add(permission)
            db.flush()
        permissions_by_code[code] = permission

    role_specs = {
        "admin": ["ip.read", "ip.write", "request.review", "audit.read", "import.run", "dashboard.read"],
        "operator": ["ip.read", "ip.write", "import.run", "dashboard.read"],
        "reviewer": ["ip.read", "request.review", "audit.read", "dashboard.read"],
        "viewer": ["ip.read", "audit.read", "dashboard.read"],
    }
    roles_by_name: dict[str, Role] = {}
    for role_name, permission_codes in role_specs.items():
        role = db.query(Role).filter(Role.name == role_name).first()
        if not role:
            role = Role(name=role_name, description=f"{role_name} role")
            db.add(role)
            db.flush()
        role.permissions = [permissions_by_code[code] for code in permission_codes]
        roles_by_name[role_name] = role

    user_specs = [
        {
            "username": "admin",
            "email": "admin@example.com",
            "full_name": "Local Admin",
            "department": "IT",
            "password": "admin123",
            "role_names": ["admin"],
            "is_superuser": True,
        },
        {
            "username": "operator1",
            "email": "operator1@example.com",
            "full_name": "Network Operator",
            "department": "Infrastructure",
            "password": "operator123",
            "role_names": ["operator"],
            "is_superuser": False,
        },
        {
            "username": "reviewer1",
            "email": "reviewer1@example.com",
            "full_name": "Request Reviewer",
            "department": "Corporate IT",
            "password": "reviewer123",
            "role_names": ["reviewer"],
            "is_superuser": False,
        },
        {
            "username": "viewer1",
            "email": "viewer1@example.com",
            "full_name": "Operations Viewer",
            "department": "PMO",
            "password": "viewer123",
            "role_names": ["viewer"],
            "is_superuser": False,
        },
    ]

    users_by_username: dict[str, User] = {}
    for spec in user_specs:
        user = db.query(User).filter(User.username == spec["username"]).first()
        if not user:
            user = User(
                username=spec["username"],
                email=spec["email"],
                full_name=spec["full_name"],
                department=spec["department"],
                hashed_password=get_password_hash(spec["password"]),
                is_active=True,
                is_superuser=spec["is_superuser"],
            )
            db.add(user)
            db.flush()
        user.roles = [roles_by_name[name] for name in spec["role_names"]]
        users_by_username[user.username] = user

    return users_by_username

