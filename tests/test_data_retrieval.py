import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from app.main import app
from app.db import get_db
from app.models import Data
from datetime import datetime

client = TestClient(app)

@pytest.fixture
def sample_data():
    return [
        Data(
            label="hum",
            measured_at=datetime(2023, 7, 25, 12, 0, 0),
            value=10.5
        )
    ]

@pytest.fixture
def sample_aggregated_data():
    return [
        {
            "label": "hum",
            "measured_at": "2023-07-25",
            "value": 10.5,
            "min_value": 10.5,
            "max_value": 10.5
        }
    ]

@pytest.fixture
async def setup_database(sample_data):
    async for db in get_db():
        async with db.begin():
            for data in sample_data:
                db.add(data)
        await db.commit()
        break

@pytest.mark.asyncio
async def test_retrieve_data(setup_database):
    response = client.get("/api/data", params={"datalogger": "hum"})
    assert response.status_code == 200
    assert response.json() == {
        "data": [
            {
                "label": "hum",
                "measured_at": "2023-07-25T12:00:00",
                "value": 10.5
            }
        ]
    }

@pytest.mark.asyncio
async def test_retrieve_data_not_found():
    response = client.get("/api/data", params={"datalogger": "hum"})
    assert response.status_code == 404
    assert response.json() == {"detail": "No data found matching the criteria."}

@pytest.mark.asyncio
async def test_retrieve_aggregated_data(setup_database, sample_aggregated_data):
    with patch("app.crud.get_aggregated_data", AsyncMock(return_value=sample_aggregated_data)):
        response = client.get("/api/summary", params={"datalogger": "hum", "span": "day"})
        assert response.status_code == 200
        assert response.json() == {
            "data": [
                {
                    "label": "hum",
                    "measured_at": "2023-07-25",
                    "value": 10.5,
                    "min_value": 10.5,
                    "max_value": 10.5
                }
            ]
        }

@pytest.mark.asyncio
async def test_retrieve_aggregated_data_not_found():
    response = client.get("/api/summary", params={"datalogger": "hum", "span": "day"})
    assert response.status_code == 404
    assert response.json() == {"detail": "No data found matching the criteria."}

@pytest.mark.asyncio
async def test_retrieve_aggregated_data_invalid_span():
    response = client.get("/api/summary", params={"datalogger": "hum", "span": "invalid_span"})
    assert response.status_code == 422
    assert "Input should be 'hour', 'day' or 'month'" in response.json()["detail"][0]["msg"]
