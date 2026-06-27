from typing import List, Optional

from pydantic import BaseModel


class BasicStats(BaseModel):
    mean: float
    median: float
    variance: float
    std_dev: float
    minimum: float
    maximum: float


class HistogramData(BaseModel):
    bins: List[str]
    counts: List[int]


class StatisticsResponse(BaseModel):
    session_id: str

    sample_count: int

    latency_stats: BasicStats
    jitter_stats: BasicStats
    download_stats: BasicStats
    packet_loss_stats: BasicStats

    lambda_rate: float

    traffic_trend: str

    latency_histogram: Optional[HistogramData] = None
    throughput_histogram: Optional[HistogramData] = None

    analysis_message: str