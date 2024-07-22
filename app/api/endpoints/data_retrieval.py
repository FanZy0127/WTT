from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud import get_data, get_aggregated_data
from app.db import get_db
from app.schemas import DataRetrievalResponse, AggregatedDataRetrievalResponse
from typing import Optional

router = APIRouter()

@router.get("/data", response_model=DataRetrievalResponse)
async def retrieve_data(
    datalogger: str = Query(...),
    since: Optional[str] = Query(None),
    before: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
) -> DataRetrievalResponse:
    data = await get_data(db, datalogger, since, before)
    if not data:
        raise HTTPException(status_code=404, detail="No data found matching the criteria.")
    return {"data": data}

@router.get("/summary", response_model=AggregatedDataRetrievalResponse)
async def retrieve_aggregated_data(
    datalogger: str = Query(...),
    span: str = Query("day"),  # Set default span to "day" if not provided
    since: Optional[str] = Query(None),
    before: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db)
) -> AggregatedDataRetrievalResponse:
    data = await get_aggregated_data(db, datalogger, span, since, before)
    if not data:
        raise HTTPException(status_code=404, detail="No data found matching the criteria.")
    return {"data": data}
