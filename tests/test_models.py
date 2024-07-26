import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base, Data
from datetime import datetime

SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module")
def db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

def test_create_data_instance():
    data = Data(
        id=1,
        label="test_label",
        measured_at=datetime(2023, 7, 25, 12, 0, 0),
        value=10.5
    )
    assert data.id == 1
    assert data.label == "test_label"
    assert data.measured_at == datetime(2023, 7, 25, 12, 0, 0)
    assert data.value == 10.5

def test_data_table_attributes():
    assert Data.__tablename__ == "data"
    assert hasattr(Data, 'id')
    assert hasattr(Data, 'label')
    assert hasattr(Data, 'measured_at')
    assert hasattr(Data, 'value')

def test_data_persistence(db):
    data = Data(
        label="test_label",
        measured_at=datetime(2023, 7, 25, 12, 0, 0),
        value=10.5
    )
    db.add(data)
    db.commit()

    retrieved_data = db.query(Data).filter(Data.label == "test_label").first()
    assert retrieved_data is not None
    assert retrieved_data.label == "test_label"
    assert retrieved_data.measured_at == datetime(2023, 7, 25, 12, 0, 0)
    assert retrieved_data.value == 10.5
