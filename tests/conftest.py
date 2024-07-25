import pytest
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import delete, select, func
from app.models import Base, Data
from app.schemas import DataCreate
from datetime import datetime

DATABASE_URL_TEST = "sqlite+aiosqlite:///./test.db"

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def async_engine():
    engine = create_async_engine(DATABASE_URL_TEST, echo=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()

@pytest.fixture(scope="session")
def async_session_factory(async_engine):
    return sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )

@pytest.fixture(scope="function")
async def async_session(async_session_factory):
    async with async_session_factory() as session:
        await session.begin()
        yield session
        await session.rollback()
        await session.close()

@pytest.fixture(scope="function", autouse=True)
async def cleanup_db(async_session: AsyncSession):
    await async_session.execute(delete(Data))
    await async_session.commit()
    # Ajoutez un log pour confirmer le nettoyage de la base de données
    count_result = await async_session.execute(select(func.count(Data.id)))
    count = count_result.scalar()
    assert count == 0, f"Expected 0 records in database after cleanup, but found {count}"
    yield

@pytest.fixture
def sample_data():
    return [
        DataCreate(label="temp", measured_at=datetime(2022, 12, 31, 1, 0, 0), value=35.0),
        DataCreate(label="temp", measured_at=datetime(2022, 12, 31, 2, 0, 0), value=46.0),
        DataCreate(label="temp", measured_at=datetime(2022, 12, 31, 3, 0, 0), value=24.0),
        DataCreate(label="hum", measured_at=datetime(2022, 12, 31, 1, 0, 0), value=70.0),
        DataCreate(label="hum", measured_at=datetime(2022, 12, 31, 2, 0, 0), value=82.0),
    ]
