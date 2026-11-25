import os,sys
from pathlib import Path
os.environ["DATABASE_URL"]="sqlite://"
sys.path.insert(0,str(Path(__file__).parents[1]))
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.database import Base,get_db
from app.main import app
from app.appointment_schema import initialize_appointment_schema

@pytest.fixture
def db():
    engine=create_engine("sqlite://",connect_args={"check_same_thread":False},poolclass=StaticPool)
    Base.metadata.create_all(engine); initialize_appointment_schema(engine); Session=sessionmaker(bind=engine,expire_on_commit=False); session=Session()
    yield session; session.close()
@pytest.fixture
def client(db):
    app.dependency_overrides[get_db]=lambda:db
    with TestClient(app) as c: yield c
    app.dependency_overrides.clear()
