import os
import asyncio
import logging
import subprocess
from fastapi import FastAPI
from dotenv import load_dotenv
from app.api.endpoints import data_ingestion, data_retrieval
from app.db import init_db, get_db, engine
from app.api.endpoints.data_ingestion import ingest_data_from_main
from app.data_validation import extract_files, validate_json_or_yaml
from sqlalchemy.ext.asyncio import AsyncSession

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
    logging.info("Creating output directory if not exists.")
    os.makedirs('output', exist_ok=True)

    logging.info("Extracting files.")
    extract_files(DATA_TAR_GZ_PATH, EXTRACTED_DATA_PATH)
    validate_json_or_yaml(FILE_PATHS)

    logging.info("Starting JSON Server.")
    subprocess.Popen([JSON_SERVER_PATH, "--watch", "data/extracted/datalogger/db.json", "--port", "3000"])

    logging.info("Initializing database.")
    await init_db()

    await asyncio.sleep(2)

    async with AsyncSession(engine) as db:
        logging.info("Starting data ingestion.")
        await ingest_data_from_main(db=db)


    # logging.info("Stopping JSON Server.")
    # json_server_process.terminate()
    # await json_server_process.wait()

if __name__ == "__main__":
    import hypercorn.asyncio
    from hypercorn.config import Config

    logging.info("Starting FastAPI server with Hypercorn.")
    config = Config.from_pyfile('hypercorn_config.py')
    asyncio.run(hypercorn.asyncio.serve(app, config))
