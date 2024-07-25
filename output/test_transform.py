import pytest
from typing import Any, Dict
from app.api.endpoints.data_ingestion import fetch_data_from_json_server


@pytest.fixture
def raw_data() -> Dict[str, Any]:
    return {
        "2023-01-01T00:00:00": {"temp": 25.0, "hum": 80.0},
        "2023-01-01T01:00:00": {"temp": 26.0, "hum": 82.0},
    }


def test_fetch_data_from_json_server(monkeypatch, raw_data: Dict[str, Any]) -> None:
    def mock_requests_get(url: str) -> Any:
        class MockResponse:
            # Simulation of a succeeded request
            @staticmethod
            def raise_for_status() -> None:
                pass

            @staticmethod
            def json() -> Dict[str, Any]:
                return raw_data

        return MockResponse()

    monkeypatch.setattr("requests.get", mock_requests_get)
    transformed_data = fetch_data_from_json_server()
    assert len(transformed_data) == 4
    assert transformed_data[0] == {"label": "temp", "measured_at": "2023-01-01T00:00:00", "value": 25.0}
    assert transformed_data[1] == {"label": "hum", "measured_at": "2023-01-01T00:00:00", "value": 80.0}
