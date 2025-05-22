import unittest
from unittest.mock import patch, MagicMock, mock_open
import io
import sys
from pathlib import Path
import socket  # Biblioteca estándar
import subprocess # Para mockear subprocess.run y CalledProcessError

# Importaciones de terceros
import psutil
import requests  # Para requests.exceptions.RequestException

# Modificar sys.path para permitir la importación directa de netinfotool desde src
# Esto debe hacerse antes de importar desde netinfotool
RUTA_SRC = str(Path(__file__).resolve().parent.parent / "src")
sys.path.insert(0, RUTA_SRC)

from netinfotool import (  # noqa: E402
    obtener_informacion_red,
    guardar_informacion_red_en_archivo,
    mostrar_informacion_red,
    obtener_gateway_predeterminado,
    obtener_velocidad_internet,
)

# Mockear datetime directamente en el módulo netinfotool donde se usa
RUTA_MOCK_DATETIME = "netinfotool.datetime"
RUTA_MOCK_SUBPROCESS = "netinfotool.subprocess"
RUTA_MOCK_PLATFORM = "netinfotool.platform"

# Datos de muestra para mocking
HOSTNAME_MUESTRA = "host-prueba"
DIRECCIONES_IP_MUESTRA = ["192.168.1.101", "10.0.0.1"]
IP_EXTERNA_MUESTRA = "8.8.8.8"
GATEWAY_MUESTRA = "192.168.1.254"
DATOS_INTERFAZ_MUESTRA = {
    "eth0": [
        MagicMock(family=socket.AF_INET, address="192.168.1.101"),
        MagicMock(family=socket.AF_INET6, address="fe80::1"),
        MagicMock(family=psutil.AF_LINK, address="00:1B:44:11:3A:B7"),  # type: ignore
    ],
    "lo": [
        MagicMock(family=socket.AF_INET, address="127.0.0.1"),
        MagicMock(family=socket.AF_INET6, address="::1"),
    ],
}
DATOS_VELOCIDAD_MUESTRA = {
    "ping": "10.0 ms",
    "descarga": "100.00 Mbit/s",
    "subida": "50.00 Mbit/s",
    "error": None,
}
DATOS_VELOCIDAD_ERROR_MUESTRA = {
    "ping": None, "descarga": None, "subida": None, "error": "Error en prueba de velocidad"
}


class TestObtenerInformacionRed(unittest.TestCase):
    @patch("netinfotool.obtener_gateway_predeterminado", return_value=GATEWAY_MUESTRA)
    @patch("netinfotool.psutil.net_if_addrs", return_value=DATOS_INTERFAZ_MUESTRA)
    @patch("netinfotool.requests.get")
    @patch(
        "netinfotool.socket.gethostbyname_ex",
        return_value=(HOSTNAME_MUESTRA, [], DIRECCIONES_IP_MUESTRA),
    )
    @patch("netinfotool.socket.gethostname", return_value=HOSTNAME_MUESTRA)
    def test_recuperacion_exitosa_datos_completos(
        self,
        mock_gethostname,
        mock_gethostbyname_ex,
        mock_requests_get,
        mock_net_if_addrs,
        mock_obtener_gateway,
    ):
        mock_requests_get.return_value = MagicMock(text=IP_EXTERNA_MUESTRA)
        informacion_esperada = {
            "hostname": HOSTNAME_MUESTRA,
            "direcciones_ip": DIRECCIONES_IP_MUESTRA,
            "ip_externa": IP_EXTERNA_MUESTRA,
            "gateway_predeterminado": GATEWAY_MUESTRA,
            "interfaces": {
                "eth0": {
                    "ipv4": ["192.168.1.101"],
                    "ipv6": ["fe80::1"],
                    "mac": ["00:1B:44:11:3A:B7"],
                },
                "lo": {"ipv4": ["127.0.0.1"], "ipv6": ["::1"], "mac": []},
            },
        }
        informacion = obtener_informacion_red()
        self.assertEqual(informacion, informacion_esperada)
        mock_obtener_gateway.assert_called_once()


class TestGuardarInformacionRedEnArchivo(unittest.TestCase):
    @patch(RUTA_MOCK_DATETIME)
    @patch("builtins.open", new_callable=mock_open)
    def test_guardado_exitoso_con_todos_los_datos(self, mock_file_open, mock_fecha_hora):
        datos_informacion_muestra = {
            "hostname": "host-guardado",
            "direcciones_ip": ["10.0.0.2"],
            "ip_externa": "1.2.3.4",
            "gateway_predeterminado": GATEWAY_MUESTRA,
            "velocidad_internet": DATOS_VELOCIDAD_MUESTRA,
            "interfaces": {"eth1": {"ipv4": ["10.0.0.2"], "mac": ["AA:BB:CC:DD:EE:FF"]}},
        }
        mock_now = MagicMock()
        mock_now.strftime.return_value = "20230101_120000"
        mock_fecha_hora.datetime.now.return_value = mock_now
        guardar_informacion_red_en_archivo(datos_informacion_muestra)
        nombre_archivo_esperado = Path("output") / "informacion_red_20230101_120000.txt"
        mock_file_open.assert_called_once_with(nombre_archivo_esperado, "w", encoding="utf-8")
        handle = mock_file_open()
        contenido_escrito = "".join(c[0][0] for c in handle.write.call_args_list)
        self.assertIn("Gateway Predeterminado: " + GATEWAY_MUESTRA, contenido_escrito)
        self.assertIn("Descarga: " + DATOS_VELOCIDAD_MUESTRA["descarga"], contenido_escrito)

    @patch(RUTA_MOCK_DATETIME)
    @patch("builtins.open", new_callable=mock_open)
    def test_guardado_sin_velocidad_ni_gateway(self, mock_file_open, mock_fecha_hora):
        datos_informacion_muestra = {
            "hostname": "host-simple", "direcciones_ip": [], "ip_externa": "N/D",
            "gateway_predeterminado": None, "interfaces": {}
        } # No incluye 'velocidad_internet'
        mock_now = MagicMock(); mock_now.strftime.return_value = "20230101_120001"
        mock_fecha_hora.datetime.now.return_value = mock_now
        guardar_informacion_red_en_archivo(datos_informacion_muestra)
        contenido_escrito = "".join(c[0][0] for c in mock_file_open().write.call_args_list)
        self.assertIn("Gateway Predeterminado: None", contenido_escrito) # Changed N/D to None
        self.assertNotIn("Velocidad de Internet:", contenido_escrito)


class TestMostrarInformacionRed(unittest.TestCase):
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_salida_con_todos_los_datos(self, mock_stdout):
        datos_informacion_muestra = {
            "hostname": "host-mostrar", "direcciones_ip": ["192.168.0.10"], "ip_externa": "5.6.7.8",
            "gateway_predeterminado": GATEWAY_MUESTRA, "velocidad_internet": DATOS_VELOCIDAD_MUESTRA,
            "interfaces": {"wlan0": {"ipv4": ["192.168.0.10"], "mac": ["11:22:33:44:55:66"]}}
        }
        mostrar_informacion_red(datos_informacion_muestra)
        salida = mock_stdout.getvalue()
        self.assertIn("Gateway Predeterminado: " + GATEWAY_MUESTRA, salida)
        self.assertIn("Descarga: " + DATOS_VELOCIDAD_MUESTRA["descarga"], salida)

    @patch("sys.stdout", new_callable=io.StringIO)
    def test_salida_con_error_velocidad(self, mock_stdout):
        datos_informacion_muestra = {
            "hostname": "host-error-velocidad", "direcciones_ip": [], "ip_externa": "N/D",
            "gateway_predeterminado": None, "velocidad_internet": DATOS_VELOCIDAD_ERROR_MUESTRA,
            "interfaces": {}
        }
        mostrar_informacion_red(datos_informacion_muestra)
        salida = mock_stdout.getvalue()
        self.assertIn("Error: Error en prueba de velocidad", salida)


class TestObtenerGatewayPredeterminado(unittest.TestCase):
    @patch(RUTA_MOCK_PLATFORM + ".system")
    @patch(RUTA_MOCK_SUBPROCESS + ".run")
    def test_gateway_linux_exitoso(self, mock_run, mock_system):
        mock_system.return_value = "linux"
        mock_run.return_value = MagicMock(stdout="default via 192.168.1.254 dev eth0")
        self.assertEqual(obtener_gateway_predeterminado(), "192.168.1.254")

    @patch(RUTA_MOCK_PLATFORM + ".system")
    @patch(RUTA_MOCK_SUBPROCESS + ".run")
    def test_gateway_windows_exitoso(self, mock_run, mock_system):
        mock_system.return_value = "windows"
        mock_run.return_value = MagicMock(stdout="          0.0.0.0          0.0.0.0    192.168.1.1    192.168.1.100     25")
        self.assertEqual(obtener_gateway_predeterminado(), "192.168.1.1")

    @patch(RUTA_MOCK_PLATFORM + ".system")
    @patch(RUTA_MOCK_SUBPROCESS + ".run")
    def test_gateway_macos_exitoso(self, mock_run, mock_system):
        mock_system.return_value = "darwin"
        mock_run.return_value = MagicMock(stdout="default 10.0.0.1 UGSc en0")
        self.assertEqual(obtener_gateway_predeterminado(), "10.0.0.1")

    @patch(RUTA_MOCK_PLATFORM + ".system", return_value="linux")
    @patch(RUTA_MOCK_SUBPROCESS + ".run", side_effect=subprocess.CalledProcessError(1, "cmd"))
    def test_gateway_comando_falla(self, mock_run, mock_system):
        self.assertIsNone(obtener_gateway_predeterminado())

    @patch(RUTA_MOCK_PLATFORM + ".system", return_value="sunos")
    def test_gateway_os_no_soportado(self, mock_system):
        self.assertIsNone(obtener_gateway_predeterminado())


class TestObtenerVelocidadInternet(unittest.TestCase):
    @patch(RUTA_MOCK_SUBPROCESS + ".run")
    def test_velocidad_exitosa(self, mock_run):
        mock_run.return_value = MagicMock(
            stdout="Ping: 12.345 ms\nDownload: 123.45 Mbit/s\nUpload: 12.34 Mbit/s",
            returncode=0, text=True, encoding="utf-8"
        )
        resultados = obtener_velocidad_internet()
        self.assertEqual(resultados["ping"], "12.345 ms")
        self.assertEqual(resultados["descarga"], "123.45 Mbit/s")
        self.assertEqual(resultados["subida"], "12.34 Mbit/s")
        self.assertIsNone(resultados["error"])

    @patch(RUTA_MOCK_SUBPROCESS + ".run", side_effect=FileNotFoundError)
    def test_velocidad_speedtest_no_encontrado(self, mock_run):
        resultados = obtener_velocidad_internet()
        self.assertIn("speedtest-cli no encontrado", resultados["error"])

    @patch(RUTA_MOCK_SUBPROCESS + ".run")
    def test_velocidad_speedtest_falla_ejecucion(self, mock_run):
        mock_run.side_effect = subprocess.CalledProcessError(1, "cmd", stderr="Fallo de red")
        resultados = obtener_velocidad_internet()
        self.assertIn("speedtest-cli falló", resultados["error"])
        self.assertIn("Fallo de red", resultados["error"])

    @patch(RUTA_MOCK_SUBPROCESS + ".run")
    def test_velocidad_salida_no_parseable(self, mock_run):
        mock_run.return_value = MagicMock(stdout="Salida inesperada", returncode=0, text=True, encoding="utf-8")
        resultados = obtener_velocidad_internet()
        self.assertIn("No se pudieron parsear los resultados", resultados["error"])


if __name__ == "__main__":
    unittest.main()
