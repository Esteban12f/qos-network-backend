import statistics
from typing import List

from app.repositories.measurements_repository import measurements_repository
from app.schemas.statistics import (
    BasicStats,
    HistogramData,
    StatisticsResponse,
)


class StatisticsService:
    """
    Servicio encargado de aplicar análisis estadístico sobre las mediciones.
    """

    def get_statistics(self, session_id: str) -> StatisticsResponse | None:
        history = measurements_repository.get_history(session_id)

        if not history:
            return None

        latency_values = [item["latency_ms"] for item in history]
        jitter_values = [item["jitter_ms"] for item in history]
        download_values = [item["download_mbps"] for item in history]
        packet_loss_values = [item["packet_loss_pct"] for item in history]

        lambda_rate = self._calculate_lambda_rate(history)
        traffic_trend = self._calculate_trend(latency_values)

        return StatisticsResponse(
            session_id=session_id,
            sample_count=len(history),

            latency_stats=self._calculate_basic_stats(latency_values),
            jitter_stats=self._calculate_basic_stats(jitter_values),
            download_stats=self._calculate_basic_stats(download_values),
            packet_loss_stats=self._calculate_basic_stats(packet_loss_values),

            lambda_rate=lambda_rate,
            traffic_trend=traffic_trend,

            latency_histogram=self._build_histogram(latency_values),
            throughput_histogram=self._build_histogram(download_values),

            analysis_message=self._build_analysis_message(
                sample_count=len(history),
                traffic_trend=traffic_trend
            )
        )

    def _calculate_basic_stats(self, values: List[float]) -> BasicStats:
        if not values:
            return BasicStats(
                mean=0,
                median=0,
                variance=0,
                std_dev=0,
                minimum=0,
                maximum=0
            )

        if len(values) == 1:
            return BasicStats(
                mean=round(values[0], 4),
                median=round(values[0], 4),
                variance=0,
                std_dev=0,
                minimum=round(values[0], 4),
                maximum=round(values[0], 4)
            )

        mean_value = statistics.mean(values)
        median_value = statistics.median(values)
        variance_value = statistics.variance(values)
        std_dev_value = statistics.stdev(values)

        return BasicStats(
            mean=round(mean_value, 4),
            median=round(median_value, 4),
            variance=round(variance_value, 4),
            std_dev=round(std_dev_value, 4),
            minimum=round(min(values), 4),
            maximum=round(max(values), 4)
        )

    def _calculate_lambda_rate(self, history: List[dict]) -> float:
        """
        λ se interpreta como tasa promedio de solicitudes de prueba por segundo.

        Como ahora el sistema funciona desde navegador, no usamos paquetes/s,
        sino solicitudes/s generadas por las pruebas web del frontend.
        """
        rates = []

        for item in history:
            duration = item.get("measurement_duration_s", 0)
            total_requests = item.get("total_requests", 0)

            if duration > 0:
                rates.append(total_requests / duration)

        if not rates:
            return 0

        return round(statistics.mean(rates), 4)

    def _calculate_trend(self, values: List[float]) -> str:
        """
        Calcula tendencia usando la latencia.
        Si la latencia sube, la calidad de red tiende a empeorar.
        """
        if len(values) < 4:
            return "INSUFICIENTE"

        midpoint = len(values) // 2

        first_half = values[:midpoint]
        second_half = values[midpoint:]

        first_mean = statistics.mean(first_half)
        second_mean = statistics.mean(second_half)

        difference_pct = ((second_mean - first_mean) / first_mean) * 100 if first_mean > 0 else 0

        if difference_pct > 10:
            return "CRECIENTE"

        if difference_pct < -10:
            return "DECRECIENTE"

        return "ESTABLE"

    def _build_histogram(self, values: List[float], bins_count: int = 5) -> HistogramData:
        if not values:
            return HistogramData(bins=[], counts=[])

        minimum = min(values)
        maximum = max(values)

        if minimum == maximum:
            label = f"{round(minimum, 2)}"
            return HistogramData(
                bins=[label],
                counts=[len(values)]
            )

        bin_size = (maximum - minimum) / bins_count

        counts = [0 for _ in range(bins_count)]
        labels = []

        for i in range(bins_count):
            start = minimum + (i * bin_size)
            end = start + bin_size
            labels.append(f"{round(start, 2)} - {round(end, 2)}")

        for value in values:
            index = int((value - minimum) / bin_size)

            if index >= bins_count:
                index = bins_count - 1

            counts[index] += 1

        return HistogramData(
            bins=labels,
            counts=counts
        )

    def _build_analysis_message(self, sample_count: int, traffic_trend: str) -> str:
        if sample_count < 5:
            return "Aún existen pocas muestras para un análisis estadístico sólido."

        if traffic_trend == "CRECIENTE":
            return "La latencia presenta una tendencia creciente, lo que puede indicar degradación progresiva de la conexión."

        if traffic_trend == "DECRECIENTE":
            return "La latencia presenta una tendencia decreciente, lo que indica una mejora reciente en la conexión."

        if traffic_trend == "ESTABLE":
            return "La conexión presenta un comportamiento relativamente estable durante la ventana analizada."

        return "Se requiere una mayor cantidad de mediciones para determinar una tendencia confiable."


statistics_service = StatisticsService()