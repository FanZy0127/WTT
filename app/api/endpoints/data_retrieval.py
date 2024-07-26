import logging
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud import get_data, get_aggregated_data
from app.db import get_db
from app.schemas import DataRetrievalResponse, AggregatedDataRetrievalResponse
from typing import Optional, Literal

router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/data", response_model=DataRetrievalResponse)
async def retrieve_data(
    datalogger: str = Query(...),
    since: Optional[str] = Query(None),
    before: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
) -> DataRetrievalResponse:
    logger.info(f"Retrieving data for datalogger: {datalogger}, since: {since}, before: {before}")
    try:
        data = await get_data(db, datalogger, since, before)
        if not data:
            logger.warning(f"No data found matching the criteria: datalogger={datalogger}, since={since}, before={before}")
            raise HTTPException(status_code=404, detail="No data found matching the criteria.")
        logger.info(f"Retrieved {len(data)} records for datalogger: {datalogger}")
        for record in data:
            record.measured_at = record.measured_at.isoformat()
        return DataRetrievalResponse(data=data)
    except HTTPException as e:
        logger.error(f"HTTP error retrieving data: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Error retrieving data: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/summary", response_model=AggregatedDataRetrievalResponse)
async def retrieve_aggregated_data(
    datalogger: str = Query(...),
    span: Literal["hour", "day", "month"] = Query("day"),
    since: Optional[str] = Query(None),
    before: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
) -> AggregatedDataRetrievalResponse:
    logger.info(f"Retrieving aggregated data for datalogger: {datalogger}, span: {span}, since: {since}, before: {before}")
    try:
        data = await get_aggregated_data(db, datalogger, span, since, before)
        if not data:
            logger.warning(f"No aggregated data found matching the criteria: datalogger={datalogger}, span={span}, since={since}, before={before}")
            raise HTTPException(status_code=404, detail="No data found matching the criteria.")
        logger.info(f"Retrieved {len(data)} aggregated records for datalogger: {datalogger} with span: {span}")
        return AggregatedDataRetrievalResponse(data=data)
    except ValueError as ve:
        logger.error(f"Invalid span value: {ve}")
        raise HTTPException(status_code=400, detail=str(ve))
    except HTTPException as e:
        logger.error(f"HTTP error retrieving aggregated data: {e.detail}")
        raise e
    except Exception as e:
        logger.error(f"Error retrieving aggregated data: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
