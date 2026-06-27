# identify_interfaces.py

import psutil
import pyshark

print("=== Interfaces Windows ===")

for interface in psutil.net_if_addrs():
    print(interface)

print("\n=== Interfaces PyShark ===")

for interface in pyshark.tshark.tshark.get_tshark_interfaces():
    print(interface)