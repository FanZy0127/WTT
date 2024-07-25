import logging
import requests
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException
from app.crud import store_data_in_db, check_duplicate_data
from app.db import get_db
from app.schemas import DataIngestionResponse, DataCreate
from app.config import settings
from app.logger import get_logger
import json
from typing import List, Dict, Any

router = APIRouter()
logger = get_logger("data_ingestion")

logger.setLevel(logging.ERROR)

def fetch_data_from_json_server() -> List[DataCreate]:
    try:
        response = requests.get(settings.DATA_URL)
        response.raise_for_status()
        raw_data = response.json()
        # logger.info(f"Number of records received: {len(raw_data)}")

        # Log the raw data for inspection, truncate if too large
        # raw_data_str = json.dumps(raw_data, indent=2)
        # if len(raw_data_str) > 1000:
        #     logger.info(f"Raw data received (truncated): {raw_data_str[:500]}...{raw_data_str[-500:]}")
        # else:
        #     logger.info(f"Raw data received: {raw_data_str}")

        transformed_data, ignored_records = transform_data(raw_data)
        # logger.info(f"Total ignored records: {ignored_records}")
        return [DataCreate(**record) for record in transformed_data]
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
                # logger.info(f"Processing record: {record}")
                if isinstance(record, dict):
                    process_record(record, transformed_data, ignored_records)
                else:
                    logger.warning(f"Ignored entry with expected dict, got {type(record).__name__}: {record}")
                    ignored_records += 1
        elif isinstance(raw_data, dict):
            # logger.info(f"Processing raw_data as dict")
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
        # logger.info(f"Timestamp: {timestamp}, Values: {values}")
        if isinstance(values, dict):
            for label, value in values.items():
                # logger.info(f"Label: {label}, Value: {value}")
                # Ensure that value is a valid float
                try:
                    value = float(value)
                    transformed_data.append({
                        'label': label,
                        'measured_at': timestamp,
                        'value': value
                    })
                except (ValueError, TypeError):
                    logger.warning(f"Ignored entry with invalid value for label {label} at {timestamp}: {value}")
                    ignored_records += 1
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
        with open('data_ingestion.log', 'r') as log_file:
            error_logs = log_file.readlines()[-5:]  # Last 5 lines of logs
        for log in error_logs:
            if log.strip():  # Ignore empty lines
                print(log)
        raise Exception(f"Error ingesting data: {str(e)}. Check server logs for more details.")
