import requests
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from app.crud import store_data_in_db, check_duplicate_data
from app.db import get_db
from app.schemas import DataIngestionResponse
from app.config import settings
import logging
from io import StringIO
import json
from typing import List, Dict, Any

router = APIRouter()

# Configure logger
log_stream = StringIO()
logging.basicConfig(stream=log_stream, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Reusable logger setup
def get_logger():
    logger = logging.getLogger("data_ingestion")
    if not logger.hasHandlers():
        handler = logging.StreamHandler(log_stream)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger

logger = get_logger()

def fetch_data_from_json_server() -> List[Dict[str, Any]]:
    try:
        response = requests.get(settings.DATA_URL)
        response.raise_for_status()
        raw_data = response.json()
        logger.info(f"Number of records received: {len(raw_data)}")

        # Log the raw data for inspection
        logger.info(f"Raw data received: {json.dumps(raw_data, indent=2)[:1000]}")  # Log only the first 1000 characters to avoid excessive logging

        transformed_data, ignored_records = transform_data(raw_data)
        logger.info(f"Total ignored records: {ignored_records}")
        return transformed_data
    except requests.RequestException as e:
        logger.error(f"Error fetching data from JSON server: {e}")
        raise HTTPException(status_code=500, detail="Error fetching data")
    except ValueError as e:
        logger.error(f"Error transforming data: {e}")
        raise HTTPException(status_code=500, detail=f"Error transforming data: {str(e)}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

def transform_data(raw_data: Any) -> (List[Dict[str, Any]], int):
    transformed_data = []
    ignored_records = 0

    try:
        if isinstance(raw_data, list):
            for record in raw_data:
                logger.info(f"Processing record: {record}")
                if isinstance(record, dict):
                    process_record(record, transformed_data, ignored_records)
                else:
                    logger.warning(f"Ignored entry with expected dict, got {type(record).__name__}: {record}")
                    ignored_records += 1
        elif isinstance(raw_data, dict):
            logger.info(f"Processing raw_data as dict")
            process_record(raw_data, transformed_data, ignored_records)
        else:
            logger.error(f"Expected list or dict, got {type(raw_data).__name__}: {raw_data}")
            raise ValueError(f"Expected list or dict, got {type(raw_data)}")
    except Exception as e:
        logger.error(f"Error transforming data: {e}")
        raise ValueError(f"Error transforming data: {str(e)}")

    return transformed_data, ignored_records

def process_record(record: Dict[str, Any], transformed_data: List[Dict[str, Any]], ignored_records: int) -> None:
    for timestamp, values in record.items():
        logger.info(f"Timestamp: {timestamp}, Values: {values}")
        if isinstance(values, dict):
            for label, value in values.items():
                logger.info(f"Label: {label}, Value: {value}")
                transformed_data.append({
                    'label': label,
                    'measured_at': timestamp,
                    'value': value
                })
        else:
            logger.warning(f"Ignored entry with expected dict, got {type(values).__name__}: {values}")
            ignored_records += 1

@router.post("/", response_model=DataIngestionResponse)
async def ingest_data(db: AsyncSession = Depends(get_db)) -> DataIngestionResponse:
    data = fetch_data_from_json_server()
    try:
        await store_data_in_db(data, db)
    except Exception as e:
        logger.error(f"Error ingesting data: {str(e)}")
        # Display a summary of errors
        print("----- ERROR LOGS -----")
        error_logs = log_stream.getvalue().split('\n')[-20:]  # Last 20 lines of logs
        for log in error_logs:
            if log.strip():  # Ignore empty lines
                print(log)
        raise HTTPException(status_code=500, detail=f"Error ingesting data: {str(e)}. Check server logs for more details.")
    return DataIngestionResponse(message="Data ingested successfully")

async def ingest_data_from_main(db: AsyncSession):
    data = fetch_data_from_json_server()

    # Check for duplicates
    duplicates = await check_duplicate_data(data, db)
    if duplicates:
        logger.info("Duplicate data found, skipping ingestion.")
        return

    try:
        await store_data_in_db(data, db)
    except Exception as e:
        logger.error(f"Error ingesting data: {str(e)}")
        # Display a summary of errors
        print("----- ERROR LOGS -----")
        error_logs = log_stream.getvalue().split('\n')[-20:]  # Last 20 lines of logs
        for log in error_logs:
            if log.strip():  # Ignore empty lines
                print(log)
        raise Exception(f"Error ingesting data: {str(e)}. Check server logs for more details.")
