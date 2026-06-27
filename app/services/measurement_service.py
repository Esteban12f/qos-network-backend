from datetime import datetime, timezone

from app.repositories.measurements_repository import measurements_repository
from app.schemas.measurement import MeasurementCreate, MeasurementResponse


class MeasurementService:
    """
    Servicio encargado de procesar las mediciones enviadas por Angular.

    El frontend mide:
    - latencia
    - jitter
    - velocidad de descarga
    - velocidad de subida
    - solicitudes fallidas
    - duración de la prueba

    Este servicio calcula métricas derivadas y guarda la medición.
    """

    def ingest_measurement(self, measurement: MeasurementCreate) -> MeasurementResponse:
        if measurement.failed_requests > measurement.total_requests:
            raise ValueError("failed_requests no puede ser mayor que total_requests")

        packet_loss_pct = round(
            (measurement.failed_requests / measurement.total_requests) * 100,
            4
        )

        server_timestamp = datetime.now(timezone.utc)

        measurement_data = {
            "session_id": measurement.session_id,
            "latency_ms": measurement.latency_ms,
            "jitter_ms": measurement.jitter_ms,
            "download_mbps": measurement.download_mbps,
            "upload_mbps": measurement.upload_mbps,
            "failed_requests": measurement.failed_requests,
            "total_requests": measurement.total_requests,
            "packet_loss_pct": packet_loss_pct,
            "measurement_duration_s": measurement.measurement_duration_s,
            "client_timestamp": measurement.client_timestamp,
            "server_timestamp": server_timestamp,
            "device_type": measurement.device_type,
            "network_type": measurement.network_type,
        }

        measurements_repository.save(
            session_id=measurement.session_id,
            measurement=measurement_data
        )

        return MeasurementResponse(
            session_id=measurement.session_id,
            latency_ms=measurement.latency_ms,
            jitter_ms=measurement.jitter_ms,
            download_mbps=measurement.download_mbps,
            upload_mbps=measurement.upload_mbps,
            failed_requests=measurement.failed_requests,
            total_requests=measurement.total_requests,
            packet_loss_pct=packet_loss_pct,
            measurement_duration_s=measurement.measurement_duration_s,
            server_timestamp=server_timestamp
        )

    def has_measurements(self, session_id: str) -> bool:
        return measurements_repository.exists(session_id)

    def clear_session(self, session_id: str) -> bool:
        return measurements_repository.clear_session(session_id)


measurement_service = MeasurementService()