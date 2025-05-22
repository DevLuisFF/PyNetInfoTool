import socket
import requests
import psutil
import datetime
from pathlib import Path
from typing import Dict, List, Any


def get_network_info() -> Dict[str, Any]:
    """Collects detailed network information of the system.

    Gathers hostname, associated IP addresses, external IP address,
    and details about network interfaces (IPv4, IPv6, MAC).
    Error messages are stored within the dictionary if issues occur.

    Returns:
        Dict[str, Any]: A dictionary containing network information.
                        Keys include 'hostname', 'ip_addresses', 'external_ip',
                        and 'interfaces'. Values under 'interfaces' are dicts
                        per interface, with 'ipv4', 'ipv6', and 'mac' lists.
                        Error messages are stored as strings for relevant keys
                        if data retrieval fails.
    """
    info: Dict[str, Any] = {
        "hostname": "",
        "ip_addresses": [],
        "external_ip": "",
        "interfaces": {},
    }
    try:
        hostname: str = socket.gethostname()
        info["hostname"] = hostname
        ip_addresses: List[str] = socket.gethostbyname_ex(hostname)[2]
        info["ip_addresses"] = ip_addresses

        try:
            info["external_ip"] = requests.get("https://api.ipify.org", timeout=5).text
        except requests.exceptions.RequestException as e:
            info["external_ip"] = f"Error: Could not retrieve external IP. Details: {e}"

        interfaces_data = psutil.net_if_addrs()
        for interface_name, addrs in interfaces_data.items():
            info["interfaces"][interface_name] = {"ipv4": [], "ipv6": [], "mac": []}
            for addr in addrs:
                if addr.family == socket.AF_INET:
                    info["interfaces"][interface_name]["ipv4"].append(addr.address)
                elif addr.family == socket.AF_INET6:
                    info["interfaces"][interface_name]["ipv6"].append(addr.address)
                elif addr.family == psutil.AF_LINK:  # type: ignore
                    info["interfaces"][interface_name]["mac"].append(addr.address)
        return info
    except socket.gaierror as e:
        info["hostname"] = f"Error: Could not retrieve host information. Details: {e}"
        # ip_addresses might be empty or partially filled if hostname was resolved but then failed.
        # external_ip and interfaces would not have been populated.
        return info
    except Exception as e:
        # Catch-all for any other unexpected errors during psutil or other calls.
        error_msg = "Unexpected error in network info gathering."
        # Break the line before the f-string part to make it shorter
        info["hostname"] = f"{error_msg} Details: {e}"
        return info


def display_network_info(info_data: Dict[str, Any]) -> None:
    """Displays the collected network information to the console.

    Args:
        info_data: A dictionary containing the network information,
                   as returned by get_network_info().
    """
    print(f"Hostname: {info_data.get('hostname', 'N/A')}")
    print("Associated IP Addresses:")
    for ip in info_data.get("ip_addresses", []):
        print(f"  - {ip}")
    print(f"External IP Address: {info_data.get('external_ip', 'N/A')}")

    print("\nDetailed Network Interface Information:")
    for interface_name, details in info_data.get("interfaces", {}).items():
        print(f"\nInterface: {interface_name}")
        for ip in details.get("ipv4", []):
            print(f"  - IP Address: {ip}")
        for ip in details.get("ipv6", []):
            print(f"  - IPv6 Address: {ip}")
        for mac in details.get("mac", []):
            print(f"  - MAC Address: {mac}")


def save_network_info_to_file(info_data: Dict[str, Any]) -> None:
    """Saves the collected network information to a timestamped text file.

    The file is saved in the 'output' directory.

    Args:
        info_data: A dictionary containing the network information,
                   as returned by get_network_info().
    """
    output_dir = Path("output")
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp: str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name: str = f"network_info_{timestamp}.txt"
    file_path: Path = output_dir / file_name

    content: List[str] = []
    content.append(f"Hostname: {info_data.get('hostname', 'N/A')}")
    content.append("Associated IP Addresses:")
    for ip in info_data.get("ip_addresses", []):
        content.append(f"  - {ip}")
    content.append(f"External IP Address: {info_data.get('external_ip', 'N/A')}")
    content.append("\nDetailed Network Interface Information:")
    for interface_name, details in info_data.get("interfaces", {}).items():
        content.append(f"\nInterface: {interface_name}")
        for ip in details.get("ipv4", []):
            content.append(f"  - IP Address: {ip}")
        for ip in details.get("ipv6", []):
            content.append(f"  - IPv6 Address: {ip}")
        for mac in details.get("mac", []):
            content.append(f"  - MAC Address: {mac}")

    try:
        with open(file_path, "w") as file:
            file.write("\n".join(content))
        print(f"Network information saved to {file_path}")
    except IOError as e:
        print(f"Error saving information to file: {e}")


def menu() -> None:
    """Displays an interactive menu for the user to choose actions."""
    while True:
        print("\n--- Menu ---")
        print("1. Display host information")
        print("2. Save information to file")
        print("3. Exit")
        choice: str = input("Select an option: ")

        if choice == "1":
            network_info = get_network_info()
            display_network_info(network_info)
        elif choice == "2":
            network_info = get_network_info()
            save_network_info_to_file(network_info)
        elif choice == "3":
            print("Exiting...")
            break
        else:
            print("Invalid option. Please try again.")


if __name__ == "__main__":
    # Ensure global imports of datetime and os are available if not already.
    # These are standard libraries and should be fine.
    # Specific type imports from typing are handled at the top.
    menu()
