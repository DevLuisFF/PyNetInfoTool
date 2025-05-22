import socket
import requests
import psutil
import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import subprocess
import platform
import re


def obtener_informacion_red() -> Dict[str, Any]:
    """Recopila información detallada de la red del sistema.

    Reúne el nombre de host, direcciones IP asociadas, dirección IP externa,
    y detalles sobre las interfaces de red (IPv4, IPv6, MAC).
    Los mensajes de error se almacenan dentro del diccionario si ocurren problemas.

    Returns:
        Dict[str, Any]: Un diccionario que contiene información de la red.
                        Las claves incluyen 'hostname', 'direcciones_ip', 'ip_externa',
                        e 'interfaces'. Los valores bajo 'interfaces' son diccionarios
                        por interfaz, con listas 'ipv4', 'ipv6', y 'mac'.
                        Los mensajes de error se almacenan como cadenas para las claves relevantes
                        si falla la recuperación de datos.
    """
    informacion: Dict[str, Any] = {
        "hostname": "",
        "direcciones_ip": [],
        "ip_externa": "",
        "interfaces": {},
        "gateway_predeterminado": None,  # Nueva clave
    }
    try:
        hostname: str = socket.gethostname()
        informacion["hostname"] = hostname
        # Obtener todas las IPs, filtrar las IPv6 locales de enlace más tarde si es necesario
        direcciones_ip: List[str] = socket.gethostbyname_ex(hostname)[2]
        informacion["direcciones_ip"] = direcciones_ip

        try:
            # Se añade un tiempo de espera para la solicitud de IP externa
            informacion["ip_externa"] = requests.get(
                "https://api.ipify.org", timeout=5
            ).text
        except requests.exceptions.RequestException as e:
            informacion[
                "ip_externa"
            ] = f"Error: No se pudo obtener la IP externa. Detalles: {e}"

        datos_interfaces = psutil.net_if_addrs()
        for nombre_interfaz, direcciones in datos_interfaces.items():
            informacion["interfaces"][nombre_interfaz] = {
                "ipv4": [],
                "ipv6": [],
                "mac": [],
            }
            for direccion in direcciones:
                if direccion.family == socket.AF_INET:
                    informacion["interfaces"][nombre_interfaz]["ipv4"].append(
                        direccion.address
                    )
                elif direccion.family == socket.AF_INET6:
                    informacion["interfaces"][nombre_interfaz]["ipv6"].append(
                        direccion.address
                    )
                elif direccion.family == psutil.AF_LINK:  # type: ignore
                    informacion["interfaces"][nombre_interfaz]["mac"].append(
                        direccion.address
                    )
        
        # Obtener gateway predeterminado
        informacion["gateway_predeterminado"] = obtener_gateway_predeterminado()

        # Obtener velocidad de internet (esto se hace aquí para que se incluya en los datos generales)
        # La notificación al usuario sobre la lentitud se manejará en el menú si se elige explícitamente.
        # Si se llama como parte de una recopilación general, puede que no queramos el mensaje aquí.
        # Por ahora, lo incluimos en los datos, y el menú decidirá si imprimir el aviso.
        # informacion["velocidad_internet"] = obtener_velocidad_internet() # Movido al menú

        return informacion
    except socket.gaierror as e:
        informacion[
            "hostname"
        ] = f"Error: No se pudo obtener la información del host. Detalles: {e}"
        # direcciones_ip podría estar vacío o parcialmente lleno si el nombre de host se resolvió pero luego falló.
        # ip_externa e interfaces no se habrían poblado.
        return informacion
    except Exception as e:
        # Captura general para cualquier otro error inesperado durante psutil u otras llamadas.
        mensaje_error = "Error inesperado durante la recopilación de información de red."
        informacion["hostname"] = f"{mensaje_error} Detalles: {e}"  # noqa: E501
        return informacion


def obtener_gateway_predeterminado() -> Optional[str]:
    """Obtiene la dirección IP del gateway predeterminado del sistema.

    Utiliza comandos específicos de la plataforma para determinar el gateway.
    Soporta Linux, Windows y macOS.

    Returns:
        Optional[str]: La dirección IP del gateway predeterminado como una cadena
                       si se encuentra, None en caso contrario o si ocurre un error.
    """
    sistema = platform.system().lower()
    try:
        if sistema == "linux":
            # Ejecuta 'ip route | grep default'
            proceso = subprocess.run(
                ["ip", "route"], capture_output=True, text=True, check=True
            )
            for linea in proceso.stdout.splitlines():
                if "default via" in linea:
                    # Extrae la IP: 'default via 192.168.1.1 dev eth0'
                    partes = linea.split()
                    return partes[2]
        elif sistema == "windows":
            # Ejecuta 'route print -4' y busca la línea con destino 0.0.0.0
            # y que no sea la interfaz de loopback o la dirección de red misma.
            proceso = subprocess.run(
                ["route", "print", "-4"], capture_output=True, text=True, check=True
            )
            # Ejemplo de línea: '          0.0.0.0          0.0.0.0      192.168.1.1    192.168.1.101     25'
            # El gateway es la tercera IP en estas líneas.
            # Evitar la IP de la interfaz (cuarta IP) si es la misma que el gateway.
            for linea in proceso.stdout.splitlines():
                if "0.0.0.0" in linea and "On-link" not in linea: # On-link no es un gateway real
                    partes = linea.split()
                    if len(partes) >= 4 and partes[0] == "0.0.0.0" and partes[1] == "0.0.0.0":
                        # Validar que es una IP
                        match = re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", partes[2])
                        if match and partes[2] != "0.0.0.0" and partes[2] != "127.0.0.1":
                             # Asegurarse de que no es la IP de la interfaz si la métrica es baja
                            if len(partes) >= 5 and partes[3] != partes[2]:
                                return partes[2]
                            # Caso donde la IP de interfaz es diferente o no está clara, pero el gateway parece válido
                            elif len(partes) < 5 :
                                return partes[2]


        elif sistema == "darwin":  # macOS
            # Ejecuta 'netstat -nr | grep default'
            proceso = subprocess.run(
                ["netstat", "-nr"], capture_output=True, text=True, check=True
            )
            for linea in proceso.stdout.splitlines():
                if linea.startswith("default"):
                    # Ejemplo: 'default            192.168.1.1    UGSc           en0'
                    partes = linea.split()
                    if len(partes) > 1:
                        return partes[1]
        else:
            return None # Sistema operativo no soportado
    except (subprocess.CalledProcessError, FileNotFoundError, IndexError, Exception) as e:
        # Silenciar errores y devolver None si el comando falla o el parseo no funciona
        # print(f"Error al obtener gateway: {e}") # Descomentar para depuración
        return None
    return None


def mostrar_informacion_red(datos_informacion: Dict[str, Any]) -> None:
    """Muestra la información de red recopilada en la consola.

    Args:
        datos_informacion: Un diccionario que contiene la información de red,
                           devuelto por obtener_informacion_red().
    """
    print(f"Hostname: {datos_informacion.get('hostname', 'N/D')}")
    print("Direcciones IP asociadas:")
    for ip in datos_informacion.get("direcciones_ip", []):
        print(f"  - {ip}")
    print(f"Dirección IP externa: {datos_informacion.get('ip_externa', 'N/D')}")
    print(f"Gateway Predeterminado: {datos_informacion.get('gateway_predeterminado', 'N/D')}")

    velocidad = datos_informacion.get("velocidad_internet")
    if velocidad:
        print("\nVelocidad de Internet:")
        if velocidad.get("error"):
            print(f"  Error: {velocidad['error']}")
        else:
            print(f"  Ping: {velocidad.get('ping', 'N/D')}")
            print(f"  Descarga: {velocidad.get('descarga', 'N/D')}")
            print(f"  Subida: {velocidad.get('subida', 'N/D')}")

    print("\nInformación detallada de las interfaces de red:")
    for nombre_interfaz, detalles in datos_informacion.get("interfaces", {}).items():
        print(f"\nInterfaz: {nombre_interfaz}")
        for ip in detalles.get("ipv4", []):
            print(f"  - Dirección IP: {ip}")
        for ip in detalles.get("ipv6", []):
            print(f"  - Dirección IPv6: {ip}")
        for mac in detalles.get("mac", []):
            print(f"  - Dirección MAC: {mac}")


def guardar_informacion_red_en_archivo(datos_informacion: Dict[str, Any]) -> None:
    """Guarda la información de red recopilada en un archivo de texto con marca de tiempo.

    El archivo se guarda en el directorio 'output'.

    Args:
        datos_informacion: Un diccionario que contiene la información de red,
                           devuelto por obtener_informacion_red().
    """
    directorio_salida = Path("output")
    directorio_salida.mkdir(parents=True, exist_ok=True)

    marca_tiempo: str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    nombre_archivo: str = f"informacion_red_{marca_tiempo}.txt"
    ruta_archivo: Path = directorio_salida / nombre_archivo

    contenido: List[str] = []
    contenido.append(f"Hostname: {datos_informacion.get('hostname', 'N/D')}")
    contenido.append("Direcciones IP asociadas:")
    for ip in datos_informacion.get("direcciones_ip", []):
        contenido.append(f"  - {ip}")
    contenido.append(
        f"Dirección IP externa: {datos_informacion.get('ip_externa', 'N/D')}"
    )
    contenido.append(
        f"Gateway Predeterminado: {datos_informacion.get('gateway_predeterminado', 'N/D')}"
    )

    velocidad = datos_informacion.get("velocidad_internet")
    if velocidad:
        contenido.append("\nVelocidad de Internet:")
        if velocidad.get("error"):
            contenido.append(f"  Error: {velocidad['error']}")
        else:
            contenido.append(f"  Ping: {velocidad.get('ping', 'N/D')}")
            contenido.append(f"  Descarga: {velocidad.get('descarga', 'N/D')}")
            contenido.append(f"  Subida: {velocidad.get('subida', 'N/D')}")

    contenido.append("\nInformación detallada de las interfaces de red:")
    for nombre_interfaz, detalles in datos_informacion.get("interfaces", {}).items():
        contenido.append(f"\nInterfaz: {nombre_interfaz}")
        for ip in detalles.get("ipv4", []):
            contenido.append(f"  - Dirección IP: {ip}")
        for ip in detalles.get("ipv6", []):
            contenido.append(f"  - Dirección IPv6: {ip}")
        for mac in detalles.get("mac", []):
            contenido.append(f"  - Dirección MAC: {mac}")

    try:
        with open(ruta_archivo, "w", encoding="utf-8") as archivo:
            archivo.write("\n".join(contenido))
        print(f"Información de red guardada en {ruta_archivo}")
    except IOError as e:
        print(f"Error al guardar la información en el archivo: {e}")


def menu_principal() -> None:
    """Muestra un menú interactivo para que el usuario elija acciones."""
    while True:
        print("\n--- Menú Principal ---")
        print("1. Mostrar toda la información del host (incluye prueba de velocidad)")
        print("2. Guardar toda la información en archivo (incluye prueba de velocidad)")
        print("3. Realizar solo prueba de velocidad de internet")
        print("4. Mostrar solo información de Gateway")
        print("5. Salir")
        opcion: str = input("Seleccione una opción: ")

        if opcion == "1":
            print("\nObteniendo información base del host...")
            informacion_red = obtener_informacion_red()
            print("Realizando prueba de velocidad de internet... Esto puede tardar unos momentos.")
            informacion_red["velocidad_internet"] = obtener_velocidad_internet()
            mostrar_informacion_red(informacion_red)
        elif opcion == "2":
            print("\nObteniendo información base del host...")
            informacion_red = obtener_informacion_red()
            print("Realizando prueba de velocidad de internet... Esto puede tardar unos momentos.")
            informacion_red["velocidad_internet"] = obtener_velocidad_internet()
            guardar_informacion_red_en_archivo(informacion_red)
        elif opcion == "3":
            print("\nRealizando prueba de velocidad de internet... Esto puede tardar unos momentos.")
            velocidad = obtener_velocidad_internet()
            # Mostrar solo la velocidad de internet
            print("\n--- Resultados de Velocidad de Internet ---")
            if velocidad.get("error"):
                print(f"  Error: {velocidad['error']}")
            else:
                print(f"  Ping: {velocidad.get('ping', 'N/D')}")
                print(f"  Descarga: {velocidad.get('descarga', 'N/D')}")
                print(f"  Subida: {velocidad.get('subida', 'N/D')}")
        elif opcion == "4":
            print("\nObteniendo información del gateway predeterminado...")
            gateway = obtener_gateway_predeterminado()
            print("\n--- Gateway Predeterminado ---")
            if gateway:
                print(f"  Gateway: {gateway}")
            else:
                print("  No se pudo determinar el gateway predeterminado o no está configurado.")
        elif opcion == "5":
            print("Saliendo...")
            break
        else:
            print("Opción no válida. Por favor, intente de nuevo.")


if __name__ == "__main__":
    # Las importaciones globales de datetime ya están en la parte superior.
    # Las importaciones de tipos específicos de 'typing' se manejan en la parte superior.
    menu_principal()


def obtener_velocidad_internet() -> Dict[str, Optional[str]]:
    """Ejecuta una prueba de velocidad de internet usando speedtest-cli.

    Intenta ejecutar 'speedtest-cli --simple' y parsea su salida
    para obtener velocidades de descarga, subida y ping.

    Returns:
        Dict[str, Optional[str]]: Un diccionario con las claves 'descarga',
                                  'subida', 'ping', y 'error'.
                                  Los valores de velocidad/ping son cadenas si tienen éxito,
                                  None si no se pueden parsear.
                                  'error' es una cadena con un mensaje de error si la prueba
                                  falla o speedtest-cli no se encuentra, None en caso contrario.
    """
    resultados: Dict[str, Optional[str]] = {
        "descarga": None,
        "subida": None,
        "ping": None,
        "error": None,
    }
    try:
        # Ejecutar speedtest-cli
        # Usar python -m speedtest para asegurar que se usa el instalado en el entorno
        proceso = subprocess.run(
            ["python", "-m", "speedtest", "--simple"],
            capture_output=True,
            text=True,
            check=True, # Lanza CalledProcessError si speedtest-cli devuelve un código de error
            encoding="utf-8" # Asegurar decodificación correcta
        )
        # Parsear la salida
        # Ejemplo de salida:
        # Ping: 12.345 ms
        # Download: 123.45 Mbit/s
        # Upload: 12.34 Mbit/s
        for linea in proceso.stdout.splitlines():
            if linea.startswith("Ping:"):
                resultados["ping"] = linea.split("Ping:")[1].strip()
            elif linea.startswith("Download:"):
                resultados["descarga"] = linea.split("Download:")[1].strip()
            elif linea.startswith("Upload:"):
                resultados["subida"] = linea.split("Upload:")[1].strip()
        
        if resultados["ping"] is None and resultados["descarga"] is None and resultados["subida"] is None:
             # Si no se parseó nada, es probable que la salida no fuera la esperada.
            resultados["error"] = "No se pudieron parsear los resultados de speedtest-cli. Salida: " + proceso.stdout[:100]


    except subprocess.CalledProcessError as e:
        # speedtest-cli se ejecutó pero devolvió un error (ej. no se pudo conectar)
        error_output = e.stderr or e.stdout or "Error desconocido de speedtest-cli."
        resultados["error"] = (
            f"speedtest-cli falló (código {e.returncode}): {error_output.strip()[:100]}"
        )
    except FileNotFoundError:
        # speedtest-cli no está instalado o no se encuentra en el PATH
        resultados["error"] = (
            "speedtest-cli no encontrado. "
            "Por favor, instálelo (pip install speedtest-cli)."
        )
    except Exception as e:
        # Otros errores inesperados
        resultados["error"] = f"Error inesperado al ejecutar speedtest-cli: {e}"

    return resultados
