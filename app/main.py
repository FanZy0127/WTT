import logging
import subprocess
from fastapi import FastAPI
from app.api.endpoints import data_ingestion, data_retrieval
from app.db import init_db, get_db, engine
from app.api.endpoints.data_ingestion import ingest_data_from_main
from app.data_viz import generate_visualizations
from app.data_validation import extract_files, validate_json_or_yaml
from sqlalchemy.ext.asyncio import AsyncSession
from dotenv import load_dotenv
import os
import asyncio

app = FastAPI()

logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

DATA_TAR_GZ_PATH = 'data/202212-datalogger.tar.gz'
EXTRACTED_DATA_PATH = 'data/extracted'
FILE_PATHS = [
    'data/extracted/datalogger/db.json',
    'data/202212_api_requirements.json',
    'data/202212_openapi_spec_v1.json'
]

load_dotenv()

JSON_SERVER_PATH = os.getenv("JSON_SERVER_PATH")

app.include_router(data_ingestion.router, prefix="/ingest", tags=["data_ingestion"])
app.include_router(data_retrieval.router, prefix="/api", tags=["data"])


@app.get("/")
def read_root() -> dict:
    return {"message": "Welcome to Baptiste HARAMBOURE's data ingestion and retrieval API for Weenat's technical test."}

@app.on_event("startup")
async def startup_event():

    os.makedirs('output', exist_ok=True)

    extract_files(DATA_TAR_GZ_PATH, EXTRACTED_DATA_PATH)
    validate_json_or_yaml(FILE_PATHS)

    subprocess.Popen([JSON_SERVER_PATH, "--watch", "data/extracted/datalogger/db.json", "--port", "3000"])

    await init_db()

    await asyncio.sleep(2)

    async with AsyncSession(engine) as db:

        await ingest_data_from_main(db=db)

        await generate_visualizations(db=db)
