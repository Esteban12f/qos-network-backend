import asyncio
import threading
import time

import pyshark

from app.capture.live_metrics import live_metrics


class PacketCapture:

    def __init__(self):
        self.running = False
        self.interface = None
        self.thread = None
        self.capture = None

    def start(self, interface: str):
        # Evita iniciar varios hilos si la captura ya está corriendo
        if self.running:
            return

        self.interface = interface
        self.running = True

        self.thread = threading.Thread(
            target=self._capture_loop,
            daemon=True
        )

        self.thread.start()

    def stop(self):
        self.running = False
        live_metrics.reset()

        if self.capture is not None:
            try:
                self.capture.close()
            except Exception:
                pass
        self.capture = None

    def _capture_loop(self):
        try:
            # IMPORTANTE:
            # PyShark usa asyncio internamente.
            # Como estamos dentro de un hilo, debemos crear un event loop manualmente.
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            print("CAPTURE LOOP INICIADO")
            print(f"INTERFAZ SELECCIONADA: {self.interface}")

            self.capture = pyshark.LiveCapture(
                interface=self.interface
            )

            last_time = time.time()

            packet_counter = 0
            byte_counter = 0

            for packet in self.capture.sniff_continuously():

                if not self.running:
                    break

                packet_counter += 1

                try:
                    byte_counter += int(packet.length)
                except Exception:
                    pass

                now = time.time()

                if now - last_time >= 1:

                    live_metrics.update(
                        packets=packet_counter,
                        bytes_count=byte_counter,
                        interface=self.interface
                    )

                    print(
                        "MÉTRICAS:",
                        live_metrics.packets,
                        live_metrics.bytes,
                        live_metrics.throughput_bps
                    )

                    packet_counter = 0
                    byte_counter = 0
                    last_time = now

        except Exception as e:
            print("ERROR EN CAPTURA:", e)

        finally:
            self.running = False

            if self.capture is not None:
                try:
                    self.capture.close()
                except Exception:
                    pass

            self.capture = None


packet_capture = PacketCapture()