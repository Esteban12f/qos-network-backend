import ipaddress
import subprocess
import psutil
import pyshark


def get_interfaces():
    """
    Devuelve las interfaces detectadas por PyShark/TShark.
    """
    interfaces = pyshark.tshark.tshark.get_tshark_interfaces()

    return [
        {
            "name": interface
        }
        for interface in interfaces
    ]


def _is_valid_ipv4(ip: str) -> bool:
    """
    Valida que una IP sea útil para monitoreo real.
    Ignora loopback y direcciones APIPA 169.254.x.x.
    """
    try:
        ip_obj = ipaddress.ip_address(ip)

        if ip_obj.is_loopback:
            return False

        if ip.startswith("169.254."):
            return False

        return ip_obj.version == 4

    except ValueError:
        return False


def get_default_gateway_ip():
    """
    Obtiene la IP de la interfaz que Windows usa para salir a Internet.
    Se basa en la ruta por defecto 0.0.0.0.
    """
    result = subprocess.run(
        ["route", "print", "-4", "0.0.0.0"],
        capture_output=True,
        text=True,
        shell=True
    )

    lines = result.stdout.splitlines()

    for line in lines:
        line = line.strip()

        if line.startswith("0.0.0.0"):
            parts = line.split()

            # Formato esperado:
            # 0.0.0.0  0.0.0.0  gateway  interface_ip  metric
            if len(parts) >= 4:
                return parts[3]

    return None


def get_active_interface():
    """
    Detecta automáticamente la interfaz activa del equipo.

    Retorna el nombre amigable de Windows, por ejemplo:
    Wi-Fi 2
    Ethernet
    """
    default_interface_ip = get_default_gateway_ip()

    if not default_interface_ip:
        return None

    interfaces = psutil.net_if_addrs()

    for interface_name, addresses in interfaces.items():
        for addr in addresses:
            if addr.family.name == "AF_INET":
                ip = addr.address

                if ip == default_interface_ip and _is_valid_ipv4(ip):
                    return interface_name

    return None