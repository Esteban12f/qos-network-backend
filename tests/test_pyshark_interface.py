import pyshark

for i, interface in enumerate(pyshark.tshark.tshark.get_tshark_interfaces()):
    print(f"{i}: {interface}")