import pytest
from unittest.mock import patch, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.api.endpoints.data_ingestion import fetch_data_from_json_server, transform_data, ingest_data
from app.db import get_db
from app.schemas import DataCreate
from datetime import datetime
import httpx

from app.main import app

client = TestClient(app)

@pytest.fixture
def mock_db():
    with patch("app.db.get_db", new_callable=MagicMock) as mock_db:
        yield mock_db

@pytest.fixture
def sample_data():
    return [
        {"2023-07-25T12:00:00": {"test_label": 10.5}},
        {"2023-07-25T13:00:00": {"test_label2": 20.5}}
    ]

def test_fetch_data_from_json_server(sample_data):
    with patch("requests.get") as mock_get:
        mock_response = MagicMock()
        mock_response.json.return_value = sample_data
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        data = fetch_data_from_json_server()
        assert len(data) == 2
        assert data[0].label == "test_label"
        assert data[0].measured_at == datetime(2023, 7, 25, 12, 0, 0)
        assert data[0].value == 10.5

def test_transform_data(sample_data):
    transformed_data, ignored_records = transform_data(sample_data)
    assert len(transformed_data) == 2
    assert ignored_records == 0
    assert transformed_data[0]["label"] == "test_label"
    assert transformed_data[0]["measured_at"] == "2023-07-25T12:00:00"
    assert transformed_data[0]["value"] == 10.5

@pytest.mark.asyncio
async def test_ingest_data(mock_db, sample_data):
    async with httpx.AsyncClient(app=app, base_url="http://testserver") as ac:
        with patch("app.api.endpoints.data_ingestion.fetch_data_from_json_server", return_value=[DataCreate(label="test_label", measured_at=datetime(2023, 7, 25, 12, 0, 0), value=10.5)]):
            response = await ac.post("/ingest/")
            assert response.status_code == 200
            assert response.json() == {"message": "Data ingested successfully"}
