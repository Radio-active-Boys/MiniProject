import bluetooth

def scan_bluetooth_devices():
    nearby_devices = bluetooth.discover_devices(duration=8, lookup_names=True, lookup_class=True, device_id=-1, device_name=None, device_class=None, device_oui=None)

    if nearby_devices:
        print("Bluetooth Devices:")
        for addr, name, _ in nearby_devices:
            print(f"Address: {addr}, Name: {name}")
    else:
        print("No Bluetooth devices found.")

if __name__ == "__main__":
    scan_bluetooth_devices()