import pytest
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import DataRecord
from app.crud import store_data_in_db, get_data, get_aggregated_data


@pytest.fixture
def sample_data():
    return [
        {"label": "temp", "measured_at": 1672444800000, "value": 25.0},
        {"label": "temp", "measured_at": 1672448400000, "value": 26.0},
        {"label": "temp", "measured_at": 1672452000000, "value": 24.0},
        {"label": "hum", "measured_at": 1672444800000, "value": 80.0},
        {"label": "hum", "measured_at": 1672448400000, "value": 82.0},
    ]


@pytest.mark.asyncio
async def test_store_data_in_db(async_session: AsyncSession, sample_data):
    await store_data_in_db(sample_data, async_session)
    result = await async_session.execute(select(DataRecord))
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
    assert "min_value" in data[0]
    assert "max_value" in data[0]
    assert "avg_value" in data[0]
