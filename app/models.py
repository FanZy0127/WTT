from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class DataRecord(Base):
    __tablename__ = "data_records"
    id = Column(Integer, primary_key=True, index=True)
    label = Column(String, index=True)
    measured_at = Column(String, index=True)
    value = Column(Float)
