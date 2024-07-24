import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func, delete
from app.models import Data
from app.schemas import DataCreate
from typing import List, Optional

logger = logging.getLogger(__name__)

# Function to store data in the database
async def store_data_in_db(data: List[DataCreate], db: AsyncSession):
    try:
        db_data = [Data(**record.dict()) for record in data]
        db.add_all(db_data)
        await db.commit()
        logger.info("Data stored in the database successfully.")
    except Exception as e:
        logger.error(f"Error storing data in database: {e}")
        raise

# Function to check for duplicate data in the database
async def check_duplicate_data(data: List[DataCreate], db: AsyncSession):
    try:
        duplicates = []
        for record in data:
            query = select(Data).where(
                Data.label == record.label,
                Data.measured_at == record.measured_at,
                Data.value == record.value
            )
            result = await db.execute(query)
            if result.scalars().first():
                duplicates.append(record)
        logger.info(f"Checked for duplicates, found {len(duplicates)} duplicate records.")
        return duplicates
    except Exception as e:
        logger.error(f"Error checking for duplicate data: {e}")
        raise

# Function to get data with filters
async def get_data(db: AsyncSession, datalogger: str, since: Optional[str] = None, before: Optional[str] = None):
    try:
        query = select(Data).where(Data.label == datalogger)
        if since:
            query = query.where(Data.measured_at >= since)
        if before:
            query = query.where(Data.measured_at <= before)
        result = await db.execute(query)
        data = result.scalars().all()
        logger.info(f"Retrieved {len(data)} records from the database.")
        return data
    except Exception as e:
        logger.error(f"Error retrieving data: {e}")
        raise

# Function to get aggregated data
async def get_aggregated_data(db: AsyncSession, datalogger: str, span: str, since: Optional[str] = None,
                              before: Optional[str] = None):
    valid_spans = ["hour", "day", "month"]
    if span not in valid_spans:
        raise ValueError(f"Invalid span value. Must be one of {valid_spans}. Received '{span}'.")

    try:
        if span == "hour":
            timespan_format = "%Y-%m-%d %H:00:00"
        elif span == "day":
            timespan_format = "%Y-%m-%d"
        elif span == "month":
            timespan_format = "%Y-%m"

        query = select(
            Data.label,
            func.strftime(timespan_format, Data.measured_at).label('measured_at'),
            func.avg(Data.value).label('value'),
            func.min(Data.value).label('min_value'),
            func.max(Data.value).label('max_value')
        ).where(Data.label == datalogger)

        if since:
            query = query.where(Data.measured_at >= since)
        if before:
            query = query.where(Data.measured_at <= before)

        query = query.group_by(Data.label, 'measured_at')
        result = await db.execute(query)
        aggregated_data = result.fetchall()

        response = [
            {
                "label": record.label,
                "measured_at": record.measured_at,
                "value": record.value,
                "min_value": record.min_value,
                "max_value": record.max_value
            }
            for record in aggregated_data
        ]

        logger.info(f"Retrieved {len(aggregated_data)} aggregated records from the database.")
        return aggregated_data
    except Exception as e:
        logger.error(f"Error retrieving aggregated data: {e}")
        raise

# Function to get aggregated data by day
async def get_daily_aggregates(db: AsyncSession):
    try:
        query = select(
            Data.label,
            func.strftime("%Y-%m-%d", Data.measured_at).label('day'),
            func.avg(Data.value).label('average_value')
        ).group_by(Data.label, 'day')
        result = await db.execute(query)
        daily_aggregates = result.fetchall()
        logger.info(f"Retrieved {len(daily_aggregates)} daily aggregated records from the database.")
        return daily_aggregates
    except Exception as e:
        logger.error(f"Error retrieving daily aggregates: {e}")
        raise

# Function to get aggregated data by hour
async def get_hourly_aggregates(db: AsyncSession):
    try:
        query = select(
            Data.label,
            func.strftime("%Y-%m-%d %H:00:00", Data.measured_at).label('hour'),
            func.avg(Data.value).label('average_value')
        ).group_by(Data.label, 'hour')
        result = await db.execute(query)
        hourly_aggregates = result.fetchall()
        logger.info(f"Retrieved {len(hourly_aggregates)} hourly aggregated records from the database.")
        return hourly_aggregates
    except Exception as e:
        logger.error(f"Error retrieving hourly aggregates: {e}")
        raise

# Function to get aggregated data by label and day
async def get_aggregated_data_by_label_and_day(db: AsyncSession, label: str):
    try:
        query = select(
            func.strftime("%Y-%m-%d", Data.measured_at).label('day'),
            func.avg(Data.value).label('average_value')
        ).where(Data.label == label).group_by('day')
        result = await db.execute(query)
        aggregated_data_by_day = result.fetchall()
        logger.info(f"Retrieved {len(aggregated_data_by_day)} aggregated records by day for label '{label}' from the database.")
        return aggregated_data_by_day
    except Exception as e:
        logger.error(f"Error retrieving aggregated data by label and day: {e}")
        raise

# Function to get aggregated data by label and hour
async def get_aggregated_data_by_label_and_hour(db: AsyncSession, label: str):
    try:
        query = select(
            func.strftime("%Y-%m-%d %H:00:00", Data.measured_at).label('hour'),
            func.avg(Data.value).label('average_value')
        ).where(Data.label == label).group_by('hour')
        result = await db.execute(query)
        aggregated_data_by_hour = result.fetchall()
        logger.info(f"Retrieved {len(aggregated_data_by_hour)} aggregated records by hour for label '{label}' from the database.")
        return aggregated_data_by_hour
    except Exception as e:
        logger.error(f"Error retrieving aggregated data by label and hour: {e}")
        raise

# Function to delete all data
async def delete_all_data(db: AsyncSession):
    try:
        await db.execute(delete(Data))
        await db.commit()
        logger.info("All data deleted from the database successfully.")
    except Exception as e:
        logger.error(f"Error deleting all data: {e}")
        raise
