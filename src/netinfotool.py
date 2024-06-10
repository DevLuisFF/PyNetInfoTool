import socket
import requests
import psutil


def obtener_informacion_host():
    try:
        hostname = socket.gethostname()
        ip_addresses = socket.gethostbyname_ex(hostname)[2]

        print(f"Hostname: {hostname}")
        print("Direcciones IP asociadas:")
        for ip in ip_addresses:
            print(f"  - {ip}")

        # Obtener dirección IP externa
        try:
            external_ip = requests.get("https://api.ipify.org").text
            print(f"Dirección IP externa: {external_ip}")
        except requests.RequestException:
            print("Error: No se pudo obtener la dirección IP externa.")

        # Mostrar información detallada de la red
        print("\nInformación detallada de las interfaces de red:")
        for interface, addrs in psutil.net_if_addrs().items():
            print(f"\nInterfaz: {interface}")
            for addr in addrs:
                if addr.family == socket.AF_INET:
                    print(f"  - Dirección IP: {addr.address}")
                elif addr.family == socket.AF_INET6:
                    print(f"  - Dirección IPv6: {addr.address}")
                elif addr.family == psutil.AF_LINK:
                    print(f"  - MAC: {addr.address}")

    except socket.gaierror:
        print("Error: No se pudo obtener la información del host.")
    except Exception as e:
        print(f"Error inesperado: {e}")


def guardar_informacion_en_archivo():
    import datetime

    filename = (
        f"informacion_host_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    )
    with open(filename, "w") as file:
        # Redirigir salida estándar a archivo
        import sys

        original_stdout = sys.stdout
        sys.stdout = file
        try:
            obtener_informacion_host()
        finally:
            # Restaurar salida estándar y cerrar el archivo
            sys.stdout = original_stdout


def menu():
    while True:
        print("\n--- Menú ---")
        print("1. Mostrar información del host")
        print("2. Guardar información en archivo")
        print("3. Salir")
        opcion = input("Seleccione una opción: ")

        if opcion == "1":
            obtener_informacion_host()
        elif opcion == "2":
            guardar_informacion_en_archivo()
        elif opcion == "3":
            break
        else:
            print("Opción no válida. Por favor, intente de nuevo.")


if __name__ == "__main__":
    menu()
