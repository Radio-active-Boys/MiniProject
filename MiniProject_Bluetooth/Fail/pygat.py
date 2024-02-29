import pygatt

def enumerate_ble_devices():
    adapter = pygatt.GATTToolBackend()
    adapter.start()
    
    try:
        devices = adapter.scan(timeout=5)
        return devices
    finally:
        adapter.stop()

def run():
    ble_devices = enumerate_ble_devices()
    for address, name in ble_devices.items():
        print(f"Device [Name: {name}, Address: {address}]")

if __name__ == "__main__":
    run()
