import argparse
import json
import socket
from datetime import datetime
from typing import Any, Dict, List, Optional

import psutil
import requests


def obtener_ip_externa(timeout: float = 3.0) -> Optional[str]:
    try:
        return requests.get("https://api.ipify.org", timeout=timeout).text
    except requests.RequestException:
        return None


def obtener_informacion_host(
    incluir_ip_externa: bool = True, timeout_ip_externa: float = 3.0
) -> Dict[str, Any]:
    hostname = socket.gethostname()
    ip_addresses = socket.gethostbyname_ex(hostname)[2]
    external_ip = (
        obtener_ip_externa(timeout=timeout_ip_externa)
        if incluir_ip_externa
        else None
    )
    interfaces: List[Dict[str, Any]] = []
    stats = psutil.net_if_stats()

    for interface, addrs in psutil.net_if_addrs().items():
        ipv4 = []
        ipv6 = []
        mac = None
        for addr in addrs:
            if addr.family == socket.AF_INET:
                ipv4.append(addr.address)
            elif addr.family == socket.AF_INET6:
                ipv6.append(addr.address)
            elif addr.family == psutil.AF_LINK:
                mac = addr.address
        interface_stats = stats.get(interface)
        interfaces.append(
            {
                "nombre": interface,
                "ipv4": ipv4,
                "ipv6": ipv6,
                "mac": mac,
                "estado": {
                    "activo": interface_stats.isup if interface_stats else None,
                    "velocidad_mbps": interface_stats.speed if interface_stats else None,
                    "mtu": interface_stats.mtu if interface_stats else None,
                    "duplex": getattr(interface_stats, "duplex", None)
                    if interface_stats
                    else None,
                },
            }
        )

    return {
        "hostname": hostname,
        "ip_locales": ip_addresses,
        "ip_externa": external_ip,
        "interfaces": interfaces,
        "hora_consulta": datetime.now().isoformat(timespec="seconds"),
    }


def formatear_informacion_texto(info: Dict[str, Any]) -> str:
    lineas = [f"Hostname: {info['hostname']}"]
    lineas.append("Direcciones IP asociadas:")
    for ip in info["ip_locales"]:
        lineas.append(f"  - {ip}")
    if info["ip_externa"]:
        lineas.append(f"Dirección IP externa: {info['ip_externa']}")
    else:
        lineas.append("Dirección IP externa: No disponible.")

    lineas.append("\nInformación detallada de las interfaces de red:")
    for interface in info["interfaces"]:
        lineas.append(f"\nInterfaz: {interface['nombre']}")
        for ip in interface["ipv4"]:
            lineas.append(f"  - Dirección IP: {ip}")
        for ip in interface["ipv6"]:
            lineas.append(f"  - Dirección IPv6: {ip}")
        if interface["mac"]:
            lineas.append(f"  - MAC: {interface['mac']}")
        estado = interface["estado"]
        if estado:
            lineas.append("  - Estado:")
            for clave, valor in estado.items():
                lineas.append(f"    * {clave}: {valor}")
    lineas.append(f"\nHora de consulta: {info['hora_consulta']}")
    return "\n".join(lineas)


def guardar_informacion_en_archivo(
    info: Dict[str, Any], filename: Optional[str] = None, formato: str = "text"
) -> str:
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        extension = "json" if formato == "json" else "txt"
        filename = f"informacion_host_{timestamp}.{extension}"

    if formato == "json":
        contenido = json.dumps(info, indent=2, ensure_ascii=False)
    else:
        contenido = formatear_informacion_texto(info)

    with open(filename, "w", encoding="utf-8") as file:
        file.write(contenido)
    return filename


def mostrar_informacion(info: Dict[str, Any], formato: str = "text") -> None:
    if formato == "json":
        print(json.dumps(info, indent=2, ensure_ascii=False))
    else:
        print(formatear_informacion_texto(info))


def menu():
    while True:
        print("\n--- Menú ---")
        print("1. Mostrar información del host")
        print("2. Guardar información en archivo (texto)")
        print("3. Guardar información en archivo (JSON)")
        print("4. Salir")
        opcion = input("Seleccione una opción: ")

        if opcion in {"1", "2", "3"}:
            info = obtener_informacion_host()
        if opcion == "1":
            mostrar_informacion(info)
        elif opcion == "2":
            nombre = guardar_informacion_en_archivo(info, formato="text")
            print(f"Información guardada en {nombre}")
        elif opcion == "3":
            nombre = guardar_informacion_en_archivo(info, formato="json")
            print(f"Información guardada en {nombre}")
        elif opcion == "4":
            break
        else:
            print("Opción no válida. Por favor, intente de nuevo.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Herramienta para obtener información de red y del host."
    )
    parser.add_argument(
        "--formato",
        choices=("text", "json"),
        default="text",
        help="Formato de salida para mostrar o guardar.",
    )
    parser.add_argument(
        "--guardar",
        nargs="?",
        const="",
        help="Guardar la información en un archivo (opcionalmente indique el nombre).",
    )
    parser.add_argument(
        "--sin-ip-externa",
        action="store_true",
        help="No consultar la IP externa.",
    )
    parser.add_argument(
        "--timeout-ip-externa",
        type=float,
        default=3.0,
        help="Tiempo de espera para consultar la IP externa.",
    )
    parser.add_argument(
        "--menu",
        action="store_true",
        help="Mostrar menú interactivo.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.menu:
        menu()
    else:
        info_host = obtener_informacion_host(
            incluir_ip_externa=not args.sin_ip_externa,
            timeout_ip_externa=args.timeout_ip_externa,
        )
        mostrar_informacion(info_host, formato=args.formato)
        if args.guardar is not None:
            nombre_guardado = guardar_informacion_en_archivo(
                info_host,
                filename=args.guardar or None,
                formato=args.formato,
            )
            print(f"Información guardada en {nombre_guardado}")
