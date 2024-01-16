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
    for line in lines:
        if "SSID" in line:
            ssid = line.split(":")[1].strip()
            networks.append(ssid)
    return networks

def display_active_networks():
    while True:
        network_info = get_available_networks()
        if "Error" not in network_info:
            active_networks = parse_networks(network_info)
            print("Active Hotspots:")
            for network in active_networks:
                print(network)
        else:
            print(network_info)

        time.sleep(5)  # Wait for 5 seconds before updating again

if __name__ == "__main__":
    display_active_networks()
