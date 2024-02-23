import asyncio
import bleak
import os
import csv
from datetime import datetime

CSV_FILE_PATH = "bleak.csv"

async def run():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')  # Clear terminal

        devices = await bleak.BleakScanner.discover()
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Load existing devices from the CSV file
        existing_devices = {}
        if os.path.exists(CSV_FILE_PATH):
            with open(CSV_FILE_PATH, 'r') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    existing_devices[row[0]] = int(row[1])

        # Update devices and write to CSV
        with open(CSV_FILE_PATH, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            for device in devices:
                device_name = device.name if device.name else "Unknown"
                device_address = device.address
                print(f"Device [Name: {device_name}, Address: {device_address}]")

                # Update count for existing devices
                if device_name in existing_devices:
                    existing_devices[device_name] -= 1
                else:
                    existing_devices[device_name] = 5  # Set count to 5 for new devices

                # Write device information to CSV
                writer.writerow([current_time, device_name, device_address, existing_devices[device_name]])

        await asyncio.sleep(5)  # Wait for 5 seconds before the next scan

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
