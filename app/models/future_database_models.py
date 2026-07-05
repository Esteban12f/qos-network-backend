from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

class MeasurementDB(Base):
    __tablename__ = "measurements"

    id                     = Column(Integer,  primary_key=True, autoincrement=True)
    session_id             = Column(String,   nullable=False, index=True)
    latency_ms             = Column(Float,    nullable=False)
    jitter_ms              = Column(Float,    nullable=False)
    download_mbps          = Column(Float,    nullable=False)
    upload_mbps            = Column(Float,    nullable=True)
    failed_requests        = Column(Integer,  nullable=False, default=0)
    total_requests         = Column(Integer,  nullable=False)
    packet_loss_pct        = Column(Float,    nullable=False)
    measurement_duration_s = Column(Float,    nullable=False)
    device_type            = Column(String,   nullable=True)
    network_type           = Column(String,   nullable=True)
    client_timestamp       = Column(DateTime, nullable=True)
    server_timestamp       = Column(DateTime, nullable=False, default=datetime.utcnow)