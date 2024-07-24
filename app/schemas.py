from pydantic import BaseModel, ConfigDict
from typing import List, Optional
from datetime import datetime

class DataCreate(BaseModel):
    label: str
    measured_at: datetime
    value: float

    class Config:
        orm_mode = True

class DataRecord(BaseModel):
    label: str
    measured_at: str
    value: float

    class Config:
        from_attributes = True

    @classmethod
    def from_orm(cls, obj):
        return cls(
            label=obj.label,
            measured_at=obj.measured_at.isoformat(),  # Convert datetime to ISO format string
            value=obj.value
        )

class DataRetrievalResponse(BaseModel):
    data: List[DataRecord]

    class Config:
        model_config = ConfigDict(arbitrary_types_allowed=True)

class AggregatedDataRecord(BaseModel):
    label: str
    measured_at: str
    value: float
    min_value: Optional[float] = None
    max_value: Optional[float] = None

    class Config:
        model_config = ConfigDict(arbitrary_types_allowed=True)

    @classmethod
    def from_orm(cls, obj):
        return cls(
            label=obj.label,
            measured_at=obj.measured_at.isoformat(),  # Convert datetime to ISO format string
            value=obj.value,
            min_value=obj.min_value,
            max_value=obj.max_value
        )

class DataIngestionResponse(BaseModel):
    message: str

class AggregatedDataRetrievalResponse(BaseModel):
    data: List[AggregatedDataRecord]
