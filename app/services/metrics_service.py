from typing import Optional
from app.repositories.measurements_repository import measurements_repository
from app.schemas.metrics import (
    LiveMetricsResponse,
    MetricHistoryPoint,
    MetricsHistoryResponse,
)


class MetricsService:

    def get_live_metrics(self, session_id: str) -> Optional[LiveMetricsResponse]:
        latest = measurements_repository.get_latest(session_id)

        if latest is None:
            return None

        return LiveMetricsResponse(
            session_id=session_id,
            latency_ms=latest["latency_ms"],
            jitter_ms=latest["jitter_ms"],
            download_mbps=latest["download_mbps"],
            upload_mbps=latest.get("upload_mbps"),
            packet_loss_pct=latest["packet_loss_pct"],
            failed_requests=latest["failed_requests"],
            total_requests=latest["total_requests"],
            measurement_duration_s=latest["measurement_duration_s"],
            last_updated=latest["server_timestamp"]
        )

    def get_metrics_history(self, session_id: str) -> MetricsHistoryResponse:
        history = measurements_repository.get_history(session_id)

        points = [
            MetricHistoryPoint(
                timestamp=item["server_timestamp"],
                latency_ms=item["latency_ms"],
                jitter_ms=item["jitter_ms"],
                download_mbps=item["download_mbps"],
                upload_mbps=item.get("upload_mbps"),
                packet_loss_pct=item["packet_loss_pct"],
                failed_requests=item["failed_requests"],
                total_requests=item["total_requests"],
            )
            for item in history
        ]

        return MetricsHistoryResponse(
            session_id=session_id,
            points=points,
            total_points=len(points)
        )


metrics_service = MetricsService()