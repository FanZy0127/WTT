from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Data(Base):
    __tablename__ = "data"

    id = Column(Integer, primary_key=True, index=True)
    label = Column(String, index=True)
    measured_at = Column(DateTime, index=True)
    value = Column(Float, index=True)
