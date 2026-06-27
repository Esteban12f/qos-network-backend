import pyshark

capture = pyshark.LiveCapture(
    interface="Wi-Fi 2"
)

capture.sniff(packet_count=5)

for packet in capture:
    print(packet.highest_layer)