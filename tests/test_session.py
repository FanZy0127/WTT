import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, DateTime
import asyncio

DATABASE_URL_TEST = "sqlite+aiosqlite:///./test.db"

Base = declarative_base()

class Data(Base):
    __tablename__ = "data"
    id = Column(Integer, primary_key=True, index=True)
    label = Column(String, index=True)
    measured_at = Column(DateTime, index=True)
    value = Column(Float, index=True)

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
async def async_session_factory(async_engine):
    async_session_factory = sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )
    return async_session_factory

@pytest.fixture(scope="function")
async def async_session(async_session_factory):
    async with async_session_factory() as session:
        yield session
        await session.rollback()

@pytest.mark.asyncio
async def test_async_session(async_session):
    assert isinstance(async_session, AsyncSession), f"Expected AsyncSession, got {type(async_session)}"
