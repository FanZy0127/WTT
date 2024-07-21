from fastapi import FastAPI
from app.api.endpoints import data_ingestion, data_retrieval

app = FastAPI()

app.include_router(data_ingestion.router, prefix="/ingest", tags=["data_ingestion"])
app.include_router(data_retrieval.router, prefix="/api", tags=["data"])


@app.get("/")
def read_root() -> dict:
    return {"message": "Welcome to Baptiste HARAMBOURE's data ingestion and retrieval API for Weenat's technical test."}
