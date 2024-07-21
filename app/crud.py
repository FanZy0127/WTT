# import pandas as pd
# from sqlalchemy.ext.asyncio import AsyncSession
# from sqlalchemy.future import select
# from app.models import DataRecord
# from sqlalchemy.exc import IntegrityError
# from tqdm import tqdm
# import time
# import logging
# from datetime import datetime
# from typing import List, Optional
#
# BATCH_SIZE = 1000  # Number of records per batch
#
# logger = logging.getLogger(__name__)
#
#
# async def store_data_in_db(data: List[dict], db: AsyncSession) -> None:
#     start_time = time.time()
#     batch = []
#     total_records = len(data)
#     progress_bar = tqdm(total=total_records, unit="record", desc="Ingesting data")
#
#     try:
#         for record in data:
#             if 'measured_at' in record and 'value' in record and record['value'] is not None:
#                 measured_at_datetime = datetime.utcfromtimestamp(int(record['measured_at']) / 1000)
#                 data_record = DataRecord(
#                     label=record.get('label', 'default_label'),
#                     measured_at=measured_at_datetime.isoformat(),
#                     value=record['value']
#                 )
#                 batch.append(data_record)
#                 if len(batch) >= BATCH_SIZE:
#                     db.add_all(batch)
#                     await db.commit()
#                     progress_bar.update(len(batch))
#                     batch.clear()
#             else:
#                 logger.warning(f"Ignored record with missing or invalid value: {record}")
#
#         if batch:  # Commit remaining records
#             db.add_all(batch)
#             await db.commit()
#             progress_bar.update(len(batch))
#
#     except IntegrityError as e:
#         logger.error(f"Database integrity error: {str(e)}")
#         raise
#     except Exception as e:
#         logger.error(f"Unexpected error during data ingestion: {str(e)}")
#         raise
#
#     finally:
#         progress_bar.close()
#         elapsed_time = time.time() - start_time
#         logger.info(f"Data ingestion completed in {elapsed_time:.2f} seconds.")
#
#
# async def get_data(db: AsyncSession, label: str, since: Optional[str] = None, before: Optional[str] = None) -> List[DataRecord]:
#     query = select(DataRecord).where(DataRecord.label == label)
#     logger.info(f"Initial query: {query}")
#
#     if since:
#         query = query.where(DataRecord.measured_at >= since)
#         logger.info(f"Updated query with 'since': {query}")
#     if before:
#         query = query.where(DataRecord.measured_at <= before)
#         logger.info(f"Updated query with 'before': {query}")
#
#     logger.info(f"Final query: {query}")
#     result = await db.execute(query)
#     records = result.scalars().all()
#     records = [record for record in records if record.value is not None]
#     logger.info(f"Retrieved records: {records}")
#     return records
#
#
# async def get_aggregated_data(db: AsyncSession, label: str, span: str, since: Optional[str] = None, before: Optional[str] = None) -> List[dict]:
#     data = await get_data(db, label, since, before)
#     logger.info(f"Retrieved data: {data}")
#
#     if not data:
#         logger.warning("No data retrieved")
#         return []
#
#     df = pd.DataFrame([{
#         'measured_at': record.measured_at,
#         'value': record.value
#     } for record in data])
#     logger.info(f"DataFrame before aggregation: \n{df}")
#
#     if 'measured_at' not in df.columns:
#         logger.error("Column 'measured_at' not found in DataFrame")
#         raise KeyError("Column 'measured_at' not found in DataFrame")
#
#     df['measured_at'] = pd.to_datetime(df['measured_at'])
#
#     if span == 'day':
#         df.set_index('measured_at', inplace=True)
#         aggregated = df.resample('D').agg({
#             'value': ['min', 'max', 'mean']
#         }).reset_index()
#     elif span == 'hour':
#         df.set_index('measured_at', inplace=True)
#         aggregated = df.resample('H').agg({
#             'value': ['min', 'max', 'mean']
#         }).reset_index()
#     else:
#         aggregated = df.agg({
#             'value': ['min', 'max', 'mean']
#         }).reset_index()
#
#     aggregated.columns = ['measured_at', 'min_value', 'max_value', 'avg_value']
#     aggregated['label'] = label
#
#     aggregated['measured_at'] = aggregated['measured_at'].dt.strftime('%Y-%m-%dT%H:%M:%S')
#
#     result = []
#     for _, row in aggregated.iterrows():
#         result.append({
#             'label': row['label'],
#             'measured_at': row['measured_at'],
#             'value': {
#                 'min': row['min_value'],
#                 'max': row['max_value'],
#                 'avg': row['avg_value']
#             }
#         })
#
#     logger.info(f"Aggregated DataFrame: \n{aggregated}")
#     return result
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models import DataRecord
from sqlalchemy.exc import IntegrityError
from tqdm import tqdm
import time
import logging
from datetime import datetime
from typing import List, Optional

BATCH_SIZE = 1000  # Number of records per batch

logger = logging.getLogger(__name__)


async def store_data_in_db(data: List[dict], db: AsyncSession) -> None:
    start_time = time.time()
    batch = []
    total_records = len(data)
    progress_bar = tqdm(total=total_records, unit="record", desc="Ingesting data")

    try:
        for record in data:
            if 'measured_at' in record and 'value' in record and record['value'] is not None:
                # Ensure measured_at is in milliseconds since epoch
                if isinstance(record['measured_at'], str):
                    measured_at_datetime = datetime.fromisoformat(record['measured_at'])
                    measured_at_timestamp = int(measured_at_datetime.timestamp() * 1000)
                else:
                    measured_at_timestamp = int(record['measured_at'])

                measured_at_datetime = datetime.utcfromtimestamp(measured_at_timestamp / 1000)
                data_record = DataRecord(
                    label=record.get('label', 'default_label'),
                    measured_at=measured_at_datetime.isoformat(),
                    value=record['value']
                )
                batch.append(data_record)
                if len(batch) >= BATCH_SIZE:
                    db.add_all(batch)
                    await db.commit()
                    progress_bar.update(len(batch))
                    batch.clear()
            else:
                logger.warning(f"Ignored record with missing or invalid value: {record}")

        if batch:  # Commit remaining records
            db.add_all(batch)
            await db.commit()
            progress_bar.update(len(batch))

    except IntegrityError as e:
        logger.error(f"Database integrity error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error during data ingestion: {str(e)}")
        raise

    finally:
        progress_bar.close()
        elapsed_time = time.time() - start_time
        logger.info(f"Data ingestion completed in {elapsed_time:.2f} seconds.")


async def get_data(db: AsyncSession, label: str, since: Optional[str] = None, before: Optional[str] = None) -> List[DataRecord]:
    query = select(DataRecord).where(DataRecord.label == label)
    logger.info(f"Initial query: {query}")

    if since:
        query = query.where(DataRecord.measured_at >= since)
        logger.info(f"Updated query with 'since': {query}")
    if before:
        query = query.where(DataRecord.measured_at <= before)
        logger.info(f"Updated query with 'before': {query}")

    logger.info(f"Final query: {query}")
    result = await db.execute(query)
    records = result.scalars().all()
    records = [record for record in records if record.value is not None]
    logger.info(f"Retrieved records: {records}")
    return records


async def get_aggregated_data(db: AsyncSession, label: str, span: str, since: Optional[str] = None,
                              before: Optional[str] = None) -> List[dict]:
    data = await get_data(db, label, since, before)
    logger.info(f"Retrieved data: {data}")

    if not data:
        logger.warning("No data retrieved")
        return []

    df = pd.DataFrame([{
        'measured_at': record.measured_at,
        'value': record.value
    } for record in data])
    logger.info(f"DataFrame before aggregation: \n{df}")

    if 'measured_at' not in df.columns:
        logger.error("Column 'measured_at' not found in DataFrame")
        raise KeyError("Column 'measured_at' not found in DataFrame")

    df['measured_at'] = pd.to_datetime(df['measured_at'])

    if span == 'day':
        df.set_index('measured_at', inplace=True)
        aggregated = df.resample('D').agg({
            'value': ['min', 'max', 'mean']
        }).reset_index()
    elif span == 'hour':
        df.set_index('measured_at', inplace=True)
        aggregated = df.resample('H').agg({
            'value': ['min', 'max', 'mean']
        }).reset_index()
    else:
        aggregated = df.agg({
            'value': ['min', 'max', 'mean']
        }).reset_index()

    aggregated.columns = ['measured_at', 'min_value', 'max_value', 'avg_value']
    aggregated['label'] = label

    aggregated['measured_at'] = aggregated['measured_at'].dt.strftime('%Y-%m-%dT%H:%M:%S')

    result = []
    for _, row in aggregated.iterrows():
        result.append({
            'label': row['label'],
            'measured_at': row['measured_at'],
            'value': {
                'min': row['min_value'],
                'max': row['max_value'],
                'avg': row['avg_value']
            }
        })

    logger.info(f"Aggregated DataFrame: \n{aggregated}")
    return result
