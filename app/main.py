import subprocess
from fastapi import FastAPI
from app.api.endpoints import data_ingestion, data_retrieval
from app.db import init_db, get_db
from app.api.endpoints.data_ingestion import ingest_data_from_main
from app.data_viz import generate_visualizations
from app.data_validation import extract_files, validate_json_or_yaml
from sqlalchemy.ext.asyncio import AsyncSession

app = FastAPI()

app.include_router(data_ingestion.router, prefix="/ingest", tags=["data_ingestion"])
app.include_router(data_retrieval.router, prefix="/api", tags=["data"])


@app.get("/")
def read_root() -> dict:
    return {"message": "Welcome to Baptiste HARAMBOURE's data ingestion and retrieval API for Weenat's technical test."}

@app.on_event("startup")
async def startup_event():
    # Extract and validate data
    extract_files()
    validate_json_or_yaml()

    # Start JSON Server
    subprocess.Popen(["json-server", "--watch", "data/extracted/datalogger/db.json"])

    # Initialize the database
    await init_db()

    # Run data ingestion
    db: AsyncSession = next(get_db())
    await ingest_data_from_main(db=db)

    # Generate data visualizations
    await generate_visualizations(db=db)
