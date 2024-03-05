import subprocess
import time

def refresh_wifi_adapter():
    try:
        subprocess.run(['netsh', 'interface', 'set', 'interface', 'name="Wi-Fi"', 'admin=disable'], check=True)
        time.sleep(2)  # Wait for a few seconds
        subprocess.run(['netsh', 'interface', 'set', 'interface', 'name="Wi-Fi"', 'admin=enable'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error refreshing WiFi adapter: {e}")

def get_wifi_info():
    try:
        result = subprocess.check_output(['netsh', 'wlan', 'show', 'interfaces'])
        result = result.decode('utf-8')

        connected_info = result.find("SSID")
        if connected_info != -1:
            connected_ssid = result[connected_info:].split(":")[1].strip()
            print(f"Connected WiFi network: {connected_ssid}")
             
        else:
            print("Not connected to any WiFi network.")

        print("\nAvailable WiFi networks:")
        refresh_wifi_adapter()  # Refresh WiFi adapter to get updated list
        result = subprocess.check_output(['netsh', 'wlan', 'show', 'network'])
        result = result.decode('utf-8')

        networks = result.split("SSID")
        for network in networks[1:]:
            ssid = network.split(":")[1].strip()
            

    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_wifi_info()
