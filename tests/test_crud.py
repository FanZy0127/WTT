import pytest
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Data
from app.crud import store_data_in_db, check_duplicate_data, get_data, get_aggregated_data, get_daily_aggregates, \
    get_hourly_aggregates, get_aggregated_data_by_label_and_day, get_aggregated_data_by_label_and_hour, delete_all_data
import logging
import datetime

logger = logging.getLogger(__name__)

@pytest.mark.asyncio
async def test_store_data_in_db(async_session: AsyncSession, sample_data):
    assert isinstance(async_session, AsyncSession), f"Expected AsyncSession, got {type(async_session)}"
    await store_data_in_db(sample_data, async_session)
    result = await async_session.execute(select(Data))
    records = result.scalars().all()
    assert len(records) == len(sample_data)

@pytest.mark.asyncio
async def test_check_duplicate_data(async_session: AsyncSession, sample_data):
    assert isinstance(async_session, AsyncSession), f"Expected AsyncSession, got {type(async_session)}"
    await store_data_in_db(sample_data, async_session)

    # Intentionally duplicate the sample data to test for duplicates
    duplicates = await check_duplicate_data(sample_data, async_session)
    assert len(duplicates) == len(sample_data), "Expected to find duplicates equal to sample data length"

@pytest.mark.asyncio
async def test_get_data(async_session: AsyncSession, sample_data):
    assert isinstance(async_session, AsyncSession), f"Expected AsyncSession, got {type(async_session)}"
    await store_data_in_db(sample_data, async_session)
    data = await get_data(async_session, "temp")
    assert len(data) == 3
    data = await get_data(async_session, "hum")
    assert len(data) == 2

@pytest.mark.asyncio
async def test_get_aggregated_data(async_session: AsyncSession, sample_data):
    assert isinstance(async_session, AsyncSession), f"Expected AsyncSession, got {type(async_session)}"
    await store_data_in_db(sample_data, async_session)
    data = await get_aggregated_data(async_session, "temp", "day")
    assert len(data) > 0
    assert "value" in data[0]
    assert "min_value" in data[0]
    assert "max_value" in data[0]

@pytest.mark.asyncio
async def test_get_daily_aggregates(async_session: AsyncSession, sample_data):
    assert isinstance(async_session, AsyncSession), f"Expected AsyncSession, got {type(async_session)}"
    await store_data_in_db(sample_data, async_session)

    aggregates = await get_daily_aggregates(async_session)
    assert len(aggregates) > 0, "Expected to find daily aggregates"
    for aggregate in aggregates:
        assert aggregate.day is not None, "Expected 'day' attribute in aggregate"
        assert aggregate.average_value is not None, "Expected 'average_value' attribute in aggregate"

@pytest.mark.asyncio
async def test_get_hourly_aggregates(async_session: AsyncSession, sample_data):
    assert isinstance(async_session, AsyncSession), f"Expected AsyncSession, got {type(async_session)}"
    await store_data_in_db(sample_data, async_session)

    aggregates = await get_hourly_aggregates(async_session)
    assert len(aggregates) > 0, "Expected to find hourly aggregates"
    for aggregate in aggregates:
        assert aggregate.hour is not None, "Expected 'hour' attribute in aggregate"
        assert aggregate.average_value is not None, "Expected 'average_value' attribute in aggregate"

@pytest.mark.asyncio
async def test_get_aggregated_data_by_label_and_day(async_session: AsyncSession):
    sample_data = [
        {"label": "temp", "measured_at": datetime.datetime(2022, 9, 1, 1, 0, 0), "value": 22.0},
        {"label": "temp", "measured_at": datetime.datetime(2022, 9, 1, 2, 0, 0), "value": 24.0},
        {"label": "temp", "measured_at": datetime.datetime(2022, 9, 2, 1, 0, 0), "value": 25.0},
        {"label": "temp", "measured_at": datetime.datetime(2022, 9, 2, 2, 0, 0), "value": 26.0},
        {"label": "hum", "measured_at": datetime.datetime(2022, 9, 1, 1, 0, 0), "value": 60.0},
        {"label": "hum", "measured_at": datetime.datetime(2022, 9, 1, 2, 0, 0), "value": 65.0}
    ]

    for item in sample_data:
        async_session.add(Data(**item))
    await async_session.commit()

    label = "temp"
    aggregated_data_by_day = await get_aggregated_data_by_label_and_day(async_session, label)

    expected_results = [
        {"day": "2022-09-01", "average_value": 23.0},
        {"day": "2022-09-02", "average_value": 25.5}
    ]

    assert len(aggregated_data_by_day) == len(expected_results), "Number of results does not match"

    for result, expected in zip(aggregated_data_by_day, expected_results):
        assert result.day == expected["day"], f"Expected day {expected['day']}, got {result.day}"
        assert result.average_value == expected["average_value"], f"Expected average_value {expected['average_value']}, got {result.average_value}"

@pytest.mark.asyncio
async def test_get_aggregated_data_by_label_and_hour(async_session: AsyncSession):
    sample_data = [
        {"label": "temp", "measured_at": datetime.datetime(2022, 9, 1, 1, 0, 0), "value": 22.0},
        {"label": "temp", "measured_at": datetime.datetime(2022, 9, 1, 1, 30, 0), "value": 24.0},
        {"label": "temp", "measured_at": datetime.datetime(2022, 9, 1, 2, 0, 0), "value": 25.0},
        {"label": "temp", "measured_at": datetime.datetime(2022, 9, 1, 2, 30, 0), "value": 26.0},
        {"label": "hum", "measured_at": datetime.datetime(2022, 9, 1, 1, 0, 0), "value": 60.0},
        {"label": "hum", "measured_at": datetime.datetime(2022, 9, 1, 1, 30, 0), "value": 65.0}
    ]

    for item in sample_data:
        async_session.add(Data(**item))
    await async_session.commit()

    label = "temp"
    aggregated_data_by_hour = await get_aggregated_data_by_label_and_hour(async_session, label)

    expected_results = [
        {"hour": "2022-09-01 01:00:00", "average_value": 23.0},
        {"hour": "2022-09-01 02:00:00", "average_value": 25.5}
    ]

    assert len(aggregated_data_by_hour) == len(expected_results), "Number of results does not match"

    for result, expected in zip(aggregated_data_by_hour, expected_results):
        assert result.hour == expected["hour"], f"Expected hour {expected['hour']}, got {result.hour}"
        assert result.average_value == expected["average_value"], f"Expected average_value {expected['average_value']}, got {result.average_value}"

@pytest.mark.asyncio
async def test_delete_all_data(async_session: AsyncSession, sample_data):
    assert isinstance(async_session, AsyncSession), f"Expected AsyncSession, got {type(async_session)}"
    await store_data_in_db(sample_data, async_session)

    await delete_all_data(async_session)
    result = await async_session.execute(select(Data))
    records = result.scalars().all()
    assert len(records) == 0, "Expected all records to be deleted"
