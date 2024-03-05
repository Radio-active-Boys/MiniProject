import os
import subprocess
import time

def get_available_networks():
    try:
        result = subprocess.check_output(["netsh", "wlan", "show", "network"], universal_newlines=True)
        return result
    except subprocess.CalledProcessError:
        return "Error retrieving network information."

def parse_networks(network_info):
    networks = []
    lines = network_info.split('\n')
    ssid = bssid = None
    for line in lines:
        if "SSID" in line:
            ssid = line.split(":")[1].strip()
        elif "BSSID" in line:
            bssid = line.split(":")[1].strip()
            if ssid and bssid:
                networks.append({"SSID": ssid, "BSSID": bssid})
                ssid = bssid = None
    return networks

def display_active_networks():
    while True:
        network_info = get_available_networks()
        if "Error" not in network_info:
            active_networks = parse_networks(network_info)
            print("Active Hotspots:")
            for network in active_networks:
                print(f"SSID: {network['SSID']}, BSSID (MAC Address): {network['BSSID']}")
        else:
            print(network_info)

        time.sleep(5)  # Wait for 5 seconds before updating again

if __name__ == "__main__":
    display_active_networks()
