import unittest
from unittest.mock import patch, MagicMock, mock_open
import io
import sys
from pathlib import Path
import socket  # Standard library

# Third-party imports
import psutil
import requests  # For requests.exceptions.RequestException

# Modify sys.path to allow direct import of netinfotool from src
# This should be done before importing from netinfotool
SRC_DIR = str(Path(__file__).resolve().parent.parent / "src")
sys.path.insert(0, SRC_DIR)

from netinfotool import (  # noqa: E402
    get_network_info,
    save_network_info_to_file,
    display_network_info,
)

# Mock datetime directly in the netinfotool module where it's used
MOCK_DATETIME_PATH = "netinfotool.datetime"

# Sample data for mocking
SAMPLE_HOSTNAME = "test-host"
SAMPLE_IP_ADDRESSES = ["192.168.1.101", "10.0.0.1"]
SAMPLE_EXTERNAL_IP = "8.8.8.8"
SAMPLE_INTERFACE_DATA = {
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


class TestGetNetworkInfo(unittest.TestCase):
    @patch("netinfotool.psutil.net_if_addrs", return_value=SAMPLE_INTERFACE_DATA)
    @patch("netinfotool.requests.get")
    @patch(
        "netinfotool.socket.gethostbyname_ex",
        return_value=(SAMPLE_HOSTNAME, [], SAMPLE_IP_ADDRESSES),
    )
    @patch("netinfotool.socket.gethostname", return_value=SAMPLE_HOSTNAME)
    def test_successful_data_retrieval(
        self,
        mock_gethostname,
        mock_gethostbyname_ex,
        mock_requests_get,
        mock_net_if_addrs,
    ):
        mock_requests_get.return_value = MagicMock(text=SAMPLE_EXTERNAL_IP)
        expected_info = {
            "hostname": SAMPLE_HOSTNAME,
            "ip_addresses": SAMPLE_IP_ADDRESSES,
            "external_ip": SAMPLE_EXTERNAL_IP,
            "interfaces": {
                "eth0": {
                    "ipv4": ["192.168.1.101"],
                    "ipv6": ["fe80::1"],
                    "mac": ["00:1B:44:11:3A:B7"],
                },
                "lo": {"ipv4": ["127.0.0.1"], "ipv6": ["::1"], "mac": []},
            },
        }
        info = get_network_info()
        self.assertEqual(info, expected_info)
        mock_gethostname.assert_called_once()
        mock_gethostbyname_ex.assert_called_once_with(SAMPLE_HOSTNAME)
        mock_requests_get.assert_called_once_with("https://api.ipify.org", timeout=5)
        mock_net_if_addrs.assert_called_once()

    @patch("netinfotool.psutil.net_if_addrs", return_value=SAMPLE_INTERFACE_DATA)
    @patch("netinfotool.requests.get")
    @patch(
        "netinfotool.socket.gethostbyname_ex",
        return_value=(SAMPLE_HOSTNAME, [], SAMPLE_IP_ADDRESSES),
    )
    @patch("netinfotool.socket.gethostname", return_value=SAMPLE_HOSTNAME)
    def test_external_ip_request_fails(
        self,
        mock_gethostname,
        mock_gethostbyname_ex,
        mock_requests_get,
        mock_net_if_addrs,
    ):
        mock_requests_get.side_effect = requests.exceptions.RequestException(
            "Test Error"
        )
        info = get_network_info()
        self.assertIn("Error: Could not retrieve external IP.", info["external_ip"])
        self.assertEqual(info["hostname"], SAMPLE_HOSTNAME)

    @patch("netinfotool.psutil.net_if_addrs", return_value={})
    @patch("netinfotool.requests.get")
    @patch("netinfotool.socket.gethostbyname_ex")
    @patch(
        "netinfotool.socket.gethostname", side_effect=socket.gaierror("Test gaierror")
    )
    def test_hostname_resolution_fails_at_gethostname(
        self,
        mock_gethostname,
        mock_gethostbyname_ex,
        mock_requests_get,
        mock_net_if_addrs,
    ):
        info = get_network_info()
        self.assertIn("Error: Could not retrieve host information.", info["hostname"])
        self.assertEqual(info["ip_addresses"], [])
        self.assertEqual(info["external_ip"], "")
        self.assertEqual(info["interfaces"], {})
        mock_gethostname.assert_called_once()
        mock_gethostbyname_ex.assert_not_called()
        mock_requests_get.assert_not_called()
        mock_net_if_addrs.assert_not_called()

    @patch("netinfotool.psutil.net_if_addrs", return_value={})
    @patch("netinfotool.requests.get")
    @patch(
        "netinfotool.socket.gethostbyname_ex",
        side_effect=socket.gaierror("Test gaierror on gethostbyname_ex"),
    )
    @patch("netinfotool.socket.gethostname", return_value=SAMPLE_HOSTNAME)
    def test_hostname_resolution_fails_at_gethostbyname_ex(
        self,
        mock_gethostname,
        mock_gethostbyname_ex,
        mock_requests_get,
        mock_net_if_addrs,
    ):
        info = get_network_info()
        expected_msg = (
            "Error: Could not retrieve host information. "
            "Details: Test gaierror on gethostbyname_ex"
        )
        self.assertEqual(info["hostname"], expected_msg)
        self.assertEqual(info["ip_addresses"], [])
        self.assertEqual(info["external_ip"], "")
        self.assertEqual(info["interfaces"], {})
        mock_gethostname.assert_called_once()
        mock_gethostbyname_ex.assert_called_once_with(SAMPLE_HOSTNAME)
        mock_requests_get.assert_not_called()
        mock_net_if_addrs.assert_not_called()


class TestSaveNetworkInfoToFile(unittest.TestCase):
    @patch(MOCK_DATETIME_PATH)
    @patch("builtins.open", new_callable=mock_open)
    def test_successful_save(self, mock_file_open, mock_datetime):
        sample_info_data = {
            "hostname": "save-test-host",
            "ip_addresses": ["10.0.0.2"],
            "external_ip": "1.2.3.4",
            "interfaces": {
                "eth1": {"ipv4": ["10.0.0.2"], "ipv6": [], "mac": ["AA:BB:CC:DD:EE:FF"]}
            },
        }
        mock_now = MagicMock()
        mock_now.strftime.return_value = "20230101_120000"
        mock_datetime.datetime.now.return_value = mock_now
        save_network_info_to_file(sample_info_data)
        expected_filename = Path("output") / "network_info_20230101_120000.txt"
        mock_file_open.assert_called_once_with(expected_filename, "w")
        handle = mock_file_open()
        written_parts = [c[0][0] for c in handle.write.call_args_list]
        written_content = "".join(written_parts)
        self.assertIn("Hostname: save-test-host", written_content)
        self.assertIn("  - 10.0.0.2", written_content)
        self.assertIn("External IP Address: 1.2.3.4", written_content)
        self.assertIn("Interface: eth1", written_content)
        self.assertIn("  - IP Address: 10.0.0.2", written_content)
        self.assertIn("  - MAC Address: AA:BB:CC:DD:EE:FF", written_content)
        mock_datetime.datetime.now.assert_called_once()


class TestDisplayNetworkInfo(unittest.TestCase):
    @patch("sys.stdout", new_callable=io.StringIO)
    def test_basic_output(self, mock_stdout):
        sample_info_data = {
            "hostname": "display-test-host",
            "ip_addresses": ["192.168.0.10"],
            "external_ip": "5.6.7.8",
            "interfaces": {
                "wlan0": {
                    "ipv4": ["192.168.0.10"],
                    "ipv6": ["fd00::1"],
                    "mac": ["11:22:33:44:55:66"],
                }
            },
        }
        display_network_info(sample_info_data)
        output = mock_stdout.getvalue()
        self.assertIn("Hostname: display-test-host", output)
        self.assertIn("  - 192.168.0.10", output)
        self.assertIn("External IP Address: 5.6.7.8", output)
        self.assertIn("Interface: wlan0", output)
        self.assertIn("  - IP Address: 192.168.0.10", output)
        self.assertIn("  - IPv6 Address: fd00::1", output)
        self.assertIn("  - MAC Address: 11:22:33:44:55:66", output)


if __name__ == "__main__":
    unittest.main()
