import os

os.environ.setdefault("DATABASE_URL", "sqlite:///./shopping_test.db")

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import database as database_module


def _bootstrap_database() -> None:
    database_module.engine = create_engine(os.environ["DATABASE_URL"], future=True)
    database_module.SessionLocal = sessionmaker(bind=database_module.engine, autoflush=False, autocommit=False)
    database_module.init_db()
    database_module.seed_default_catalog()


_bootstrap_database()
