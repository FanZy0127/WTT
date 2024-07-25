import pytest
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Data
from app.crud import store_data_in_db, get_data, get_aggregated_data
from app.schemas import DataCreate
from datetime import datetime

@pytest.fixture
def sample_data():
    return [
        DataCreate(label="temp", measured_at=datetime.fromtimestamp(1672444800), value=25.0),
        DataCreate(label="temp", measured_at=datetime.fromtimestamp(1672448400), value=26.0),
        DataCreate(label="temp", measured_at=datetime.fromtimestamp(1672452000), value=24.0),
        DataCreate(label="hum", measured_at=datetime.fromtimestamp(1672444800), value=80.0),
        DataCreate(label="hum", measured_at=datetime.fromtimestamp(1672448400), value=82.0),
    ]

@pytest.mark.asyncio
async def test_store_data_in_db(async_session: AsyncSession, sample_data):
    await store_data_in_db(sample_data, async_session)
    result = await async_session.execute(select(Data))
    records = result.scalars().all()
    assert len(records) == len(sample_data)

@pytest.mark.asyncio
async def test_get_data(async_session: AsyncSession, sample_data):
    await store_data_in_db(sample_data, async_session)
    data = await get_data(async_session, "temp")
    assert len(data) == 3
    data = await get_data(async_session, "hum")
    assert len(data) == 2

@pytest.mark.asyncio
async def test_get_aggregated_data(async_session: AsyncSession, sample_data):
    await store_data_in_db(sample_data, async_session)
    data = await get_aggregated_data(async_session, "temp", "day")
    assert len(data) > 0
    assert "value" in data[0]
    assert "min_value" in data[0]
    assert "max_value" in data[0]
