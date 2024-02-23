import bluetooth 
import time


while True:
    devices = bluetooth.discover_devices(duration=8, lookup_names=True, lookup_class=True, device_id=-1, device_name=None, device_class=None, device_oui=None)
    
    if devices:
        print("Bluetooth Devices:")
        for addr, name, _ in devices:
            print(f"Address: {addr}, Name: {name}")
    else:
        print("No Bluetooth devices found.")

    time.sleep(10)  # 10 seconds delay
