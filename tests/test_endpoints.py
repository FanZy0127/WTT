import pytest
from httpx import AsyncClient
from app.main import app
from app.init_db import init_db


@pytest.fixture(scope="module")
async def async_client():
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture(scope="module", autouse=True)
async def setup_database():
    await init_db()
    yield


@pytest.mark.asyncio
async def test_ingest_data(async_client):
    response = await async_client.post("/ingest/")
    assert response.status_code == 200
    assert response.json() == {"message": "Data ingested successfully"}


@pytest.mark.asyncio
async def test_retrieve_data(async_client):
    labels = ["temp", "precip", "hum"]
    for label in labels:
        response = await async_client.get(f"/retrieve/data?label={label}")
        assert response.status_code == 200
        assert isinstance(response.json()["data"], list)


@pytest.mark.asyncio
async def test_invalid_label(async_client):
    response = await async_client.get("/retrieve/data?label=invalid_label")
    assert response.status_code == 200
    assert response.json() == {"data": []}
