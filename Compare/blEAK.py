import asyncio
import bleak
import csv
from datetime import datetime
import os

CSV_FILE_PATH = "bleak_bluetooth.csv"

async def scan_ble_devices():
    devices = await bleak.BleakScanner.discover()
    return [(device.name if device.name else "Unknown", device.address) for device in devices]

def write_to_csv(data):
    with open(CSV_FILE_PATH, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(data)

def update_device_count(existing_devices, new_devices):
    updated_devices = {}

    for name, address in new_devices:
        print(f"Device [Name: {name}, Address: {address}]")

        if name in existing_devices:
            existing_devices[name] -= 1
        else:
            existing_devices[name] = 5  # Set count to 5 for new devices

        write_to_csv([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), name, address, existing_devices[name]])

    return existing_devices

async def main():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')  # Clear terminal
        nearby_devices = await scan_ble_devices()

        # Load existing devices from the CSV file
        existing_devices = {}
        if os.path.exists(CSV_FILE_PATH):
            with open(CSV_FILE_PATH, 'r') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    existing_devices[row[1]] = int(row[3])

        # Update devices and write to CSV
        existing_devices = update_device_count(existing_devices, nearby_devices)

        await asyncio.sleep(5)  # Wait for 5 seconds before the next scan

if __name__ == "__main__":
    asyncio.run(main())
