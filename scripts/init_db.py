import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.core.db import Base, SessionLocal, engine
from scripts.generate_demo_excel import generate_all_demo_excels
from scripts.seeds import SeedContext
from scripts.seeds.operations import seed_operations
from scripts.seeds.security import seed_security
from scripts.seeds.topology import seed_topology


def seed() -> None:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        context = SeedContext(db=db)
        users_by_username = seed_security(context)
        topology_index = seed_topology(context)
        seed_operations(context, topology_index, users_by_username)
        db.commit()
        generate_all_demo_excels(Path(__file__).resolve().parents[1] / "demo")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
