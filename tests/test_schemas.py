import pytest
from datetime import datetime
from app.schemas import (
    DataCreate,
    DataRecord,
    DataRetrievalResponse,
    AggregatedDataRecord,
    DataIngestionResponse,
    AggregatedDataRetrievalResponse
)

def test_data_create():
    data = DataCreate(
        label="test_label",
        measured_at=datetime(2023, 7, 25, 12, 0, 0),
        value=10.5
    )
    assert data.label == "test_label"
    assert data.measured_at == datetime(2023, 7, 25, 12, 0, 0)
    assert data.value == 10.5
    assert DataCreate.Config.orm_mode is True

def test_data_record():
    class MockORM:
        label = "test_label"
        measured_at = datetime(2023, 7, 25, 12, 0, 0)
        value = 10.5

    mock_orm = MockORM()
    data_record = DataRecord.from_orm(mock_orm)
    assert data_record.label == "test_label"
    assert data_record.measured_at == "2023-07-25T12:00:00"
    assert data_record.value == 10.5
    assert DataRecord.Config.from_attributes is True

def test_data_retrieval_response():
    data_records = [
        DataRecord(
            label="test_label",
            measured_at="2023-07-25T12:00:00",
            value=10.5
        )
    ]
    response = DataRetrievalResponse(data=data_records)
    assert response.data == data_records

def test_aggregated_data_record():
    class MockORM:
        label = "test_label"
        measured_at = datetime(2023, 7, 25, 12, 0, 0)
        value = 10.5
        min_value = 5.0
        max_value = 15.0

    mock_orm = MockORM()
    agg_data_record = AggregatedDataRecord.from_orm(mock_orm)
    assert agg_data_record.label == "test_label"
    assert agg_data_record.measured_at == "2023-07-25T12:00:00"
    assert agg_data_record.value == 10.5
    assert agg_data_record.min_value == 5.0
    assert agg_data_record.max_value == 15.0
    assert AggregatedDataRecord.Config.model_config.get('arbitrary_types_allowed') is True

def test_data_ingestion_response():
    response = DataIngestionResponse(message="Data ingested successfully")
    assert response.message == "Data ingested successfully"

def test_aggregated_data_retrieval_response():
    agg_data_records = [
        AggregatedDataRecord(
            label="test_label",
            measured_at="2023-07-25T12:00:00",
            value=10.5,
            min_value=5.0,
            max_value=15.0
        )
    ]
    response = AggregatedDataRetrievalResponse(data=agg_data_records)
    assert response.data == agg_data_records
