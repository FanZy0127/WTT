from pydantic import BaseModel, ConfigDict
from typing import List, Optional


class DataRecord(BaseModel):
    label: str
    measured_at: str
    value: float

    class Config:
        from_attributes = True


class DataRetrievalResponse(BaseModel):
    data: List[DataRecord]

    class Config:
        model_config = ConfigDict(arbitrary_types_allowed=True)


class AggregatedDataRecord(BaseModel):
    label: str
    measured_at: str
    value: float
    min_value: Optional[float]
    max_value: Optional[float]

    class Config:
        model_config = ConfigDict(arbitrary_types_allowed=True)


class DataIngestionResponse(BaseModel):
    message: str


class AggregatedDataRetrievalResponse(BaseModel):
    data: List[AggregatedDataRecord]
