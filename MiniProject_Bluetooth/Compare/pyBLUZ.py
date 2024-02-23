import bluetooth
import time
import csv
from datetime import datetime
import os

CSV_FILE_PATH = "bluetooth.csv"

def scan_bluetooth_devices():
    return bluetooth.discover_devices(lookup_names=True)

def write_to_csv(data):
    with open(CSV_FILE_PATH, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(data)

def update_device_count(existing_devices, new_devices):
    updated_devices = {}

    for addr, name in new_devices:
        device_name = name if name else "Unknown"
        device_address = addr
        print(f"Device [Name: {device_name}, Address: {device_address}]")

        if device_name in existing_devices:
            existing_devices[device_name] -= 1
        else:
            existing_devices[device_name] = 5  # Set count to 5 for new devices

        write_to_csv([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), device_name, device_address, existing_devices[device_name]])

    return existing_devices

def main():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')  # Clear terminal
        nearby_devices = scan_bluetooth_devices()

        # Load existing devices from the CSV file
        existing_devices = {}
        if os.path.exists(CSV_FILE_PATH):
            with open(CSV_FILE_PATH, 'r') as csvfile:
                reader = csv.reader(csvfile)
                for row in reader:
                    existing_devices[row[1]] = int(row[3])

        # Update devices and write to CSV
        existing_devices = update_device_count(existing_devices, nearby_devices)

        time.sleep(5)  # Wait for 5 seconds before the next scan

if __name__ == "__main__":
    main()
