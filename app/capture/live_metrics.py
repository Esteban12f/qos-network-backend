from collections import deque
from datetime import datetime


class LiveMetrics:
    def __init__(self):
        self.packets = 0
        self.bytes = 0
        self.throughput_bps = 0
        self.throughput_mbps = 0.0
        self.capture_active = False
        self.interface = None
        self.updated_at = None

        # Guarda los últimos 60 puntos, es decir, aprox. 60 segundos
        self.history = deque(maxlen=60)

    def update(self, packets: int, bytes_count: int, interface: str | None = None):
        self.packets = packets
        self.bytes = bytes_count
        self.throughput_bps = bytes_count * 8
        self.throughput_mbps = round(self.throughput_bps / 1_000_000, 4)
        self.capture_active = True
        self.interface = interface
        self.updated_at = datetime.now()

        self.history.append({
            "timestamp": self.updated_at.isoformat(),
            "packets_per_second": self.packets,
            "bytes_per_second": self.bytes,
            "throughput_bps": self.throughput_bps,
            "throughput_mbps": self.throughput_mbps
        })

    def reset(self):
        self.packets = 0
        self.bytes = 0
        self.throughput_bps = 0
        self.throughput_mbps = 0.0
        self.capture_active = False
        self.interface = None
        self.updated_at = datetime.now()

    def get_history(self):
        return list(self.history)


live_metrics = LiveMetrics()