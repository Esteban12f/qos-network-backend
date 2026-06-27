# test_interfaces.py

import psutil

print("Interfaces detectadas:\n")

for name, addresses in psutil.net_if_addrs().items():
    print(f"INTERFAZ: {name}")

    for addr in addresses:
        print(f"   {addr.address}")

    print()