from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class LiveMetricsResponse(BaseModel):
    session_id: str
    latency_ms: float
    jitter_ms: float
    download_mbps: float
    upload_mbps: Optional[float]
    packet_loss_pct: float
    failed_requests: int
    total_requests: int
    measurement_duration_s: float
    last_updated: datetime


class MetricHistoryPoint(BaseModel):
    timestamp: datetime
    latency_ms: float
    jitter_ms: float
    download_mbps: float
    upload_mbps: Optional[float]
    packet_loss_pct: float
    failed_requests: int
    total_requests: int


class MetricsHistoryResponse(BaseModel):
    session_id: str
    points: List[MetricHistoryPoint]
    total_points: int