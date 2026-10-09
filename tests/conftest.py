import pytest
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.compiler import compiles
from geoalchemy2 import Geometry
from fastapi.testclient import TestClient

# 1. Disable GeoAlchemy2 SpatiaLite DDL operations on SQLite
import geoalchemy2.admin.dialects.sqlite as sqlite_admin
sqlite_admin.after_create = lambda table, bind, **kw: None
sqlite_admin.before_drop = lambda table, bind, **kw: None

# 2. SQLite fallback compilers for PostgreSQL specific types during pytest
@compiles(UUID, 'sqlite')
def compile_uuid_sqlite(type_, compiler, **kw):
    return "CHAR(36)"

@compiles(JSONB, 'sqlite')
def compile_jsonb_sqlite(type_, compiler, **kw):
    return "JSON"

@compiles(Geometry, 'sqlite')
def compile_geometry_sqlite(type_, compiler, **kw):
    return "TEXT"

# 3. Bypass SpatiaLite functions GeomFromEWKT / AsEWKB during SQLite tests
Geometry.bind_expression = lambda self, bindvalue: bindvalue
Geometry.column_expression = lambda self, col: col


from app.db.database import Base, get_db
from app.main import app

# In-memory SQLite database for deterministic tests
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session() -> Generator:
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session) -> Generator:
    def _override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = _override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
