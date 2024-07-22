from sqlalchemy.orm import Session
from sqlalchemy.future import select
from sqlalchemy import func
from app.models import Data
from app.schemas import DataCreate
from typing import List

# Function to store data in the database
async def store_data_in_db(data: List[DataCreate], db: Session):
    db_data = [Data(**record.dict()) for record in data]
    db.add_all(db_data)
    await db.commit()

# Function to check for duplicate data in the database
async def check_duplicate_data(data: List[DataCreate], db: Session):
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
    return duplicates

# Function to get data with pagination
async def get_data(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Data).offset(skip).limit(limit).all()

# Function to get data by label
async def get_data_by_label(db: Session, label: str):
    return db.query(Data).filter(Data.label == label).all()

# Function to get aggregated data by day
async def get_daily_aggregates(db: Session):
    return db.query(
        Data.label,
        func.date_trunc('day', Data.measured_at).label('day'),
        func.avg(Data.value).label('average_value')
    ).group_by(Data.label, 'day').all()

# Function to get aggregated data by hour
async def get_hourly_aggregates(db: Session):
    return db.query(
        Data.label,
        func.date_trunc('hour', Data.measured_at).label('hour'),
        func.avg(Data.value).label('average_value')
    ).group_by(Data.label, 'hour').all()

# Function to get aggregated data by label and day
async def get_aggregated_data_by_label_and_day(db: Session, label: str):
    return db.query(
        func.date_trunc('day', Data.measured_at).label('day'),
        func.avg(Data.value).label('average_value')
    ).filter(Data.label == label).group_by('day').all()

# Function to get aggregated data by label and hour
async def get_aggregated_data_by_label_and_hour(db: Session, label: str):
    return db.query(
        func.date_trunc('hour', Data.measured_at).label('hour'),
        func.avg(Data.value).label('average_value')
    ).filter(Data.label == label).group_by('hour').all()

# Function to delete all data
async def delete_all_data(db: Session):
    db.query(Data).delete()
    await db.commit()
