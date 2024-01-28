import os
import asyncio
import threading
from datetime import datetime
from bleak import BleakScanner
from flask import Flask, jsonify
from pymongo import MongoClient
from dotenv import load_dotenv
import time
import keyboard

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# MongoDB setup
mongodb_uri = os.getenv("MONGODB_URI")
client = MongoClient(mongodb_uri)
db = client["bluetooth"]
collection = db["test3"]

# Dictionary to store devices currently in range along with their entry times and states
devices_in_range = {}

# List to store devices from the previous scan
previous_scan_devices = []

# Lock to ensure thread safety when modifying the dictionary
lock = threading.Lock()

# Thread function to update exit times for devices that are no longer in range
def update_exit_times():
    while True:
        with lock:
            current_time = int(datetime.now().timestamp())
            for mac_address, device_data in list(devices_in_range.items()):
                if device_data['in_range'] and not device_data['active']:
                    # 4. Update the exit time in the database only if the device is not in the active list
                    if device_data['exit_time'] == 0:
                        collection.update_one(
                            {"MAC_add": mac_address},
                            {"$push": {"Exit_time": current_time}}
                        )
                        device_data['exit_time'] = current_time
                        device_data['active'] = True  # Set the device as active

                # 4. Remove the device from the in-range dictionary if it's no longer in range
                if current_time - device_data['last_seen'] > 20:
                    if not device_data['active']:
                        if device_data['exit_time'] == 0:
                            # 4. Update exit time in the database if not already updated
                            collection.update_one(
                                {"MAC_add": mac_address},
                                {"$push": {"Exit_time": current_time}}
                            )
                            device_data['exit_time'] = current_time
                    del devices_in_range[mac_address]
                    continue

        # Sleep for a certain interval before checking again
        # Adjust the sleep duration based on your requirements
        time.sleep(10)

# Async function to discover Bluetooth devices
async def discover_devices():
    global previous_scan_devices
    while not keyboard.is_pressed('q'):
        devices = await BleakScanner.discover()
        current_scan_devices = set()
        for device in devices:
            mac_address = device.address
            current_time = int(datetime.now().timestamp())

            with lock:
                current_scan_devices.add(mac_address)
                if mac_address not in devices_in_range and mac_address not in previous_scan_devices:
                    # 1. If the device is not already in range and not in the previous scan, add it to the dictionary with entry and exit time
                    devices_in_range[mac_address] = {
                        'entry_time': 0,  # Initialize entry time to 0 for new entry
                        'exit_time': 0,
                        'in_range': True,
                        'active': False,
                        'last_seen': current_time
                    }

                    # Check if the device already exists in the database
                    existing_device = collection.find_one({"MAC_add": mac_address})

                    if existing_device:
                        # 2. If the device exists, get its entry and exit times
                        entry_times = existing_device.get("Entry_time", [])
                        exit_times = existing_device.get("Exit_time", [])

                        if not entry_times and not exit_times:
                            # New device, set entry time and insert into the database
                            devices_in_range[mac_address]['entry_time'] = current_time
                            collection.update_one(
                                {"MAC_add": mac_address},
                                {"$set": {"Entry_time": [current_time]}}
                            )
                        elif exit_times and devices_in_range[mac_address]['exit_time'] != exit_times[-1]:
                            # Device disconnected and reappeared
                            # Update entry time and insert into the database
                            devices_in_range[mac_address]['entry_time'] = current_time
                            collection.update_one(
                                {"MAC_add": mac_address},
                                {"$push": {"Entry_time": current_time}}
                            )
                        # If only exit_times is present, it's a new device entry
                    else:
                        # 3. If the device does not exist, create a new document in the database
                        new_device = {
                            "MAC_add": mac_address,
                            "Entry_time": [current_time],
                            "Exit_time": []  # 3. Initialize exit_time array
                        }
                        collection.insert_one(new_device)

                # 3. Check if the device is already in range
                elif devices_in_range[mac_address]['in_range']:
                    # Update the last seen time
                    devices_in_range[mac_address]['last_seen'] = current_time

        # 4. Check devices from the previous scan that are not in the current scan
        with lock:
            for mac_address, device_data in list(devices_in_range.items()):
                if device_data['in_range'] and mac_address not in current_scan_devices:
                    if not device_data['active']:
                        if device_data['exit_time'] == 0:
                            # 4. Update exit time in the database if not already updated
                            collection.update_one(
                                {"MAC_add": mac_address},
                                {"$push": {"Exit_time": current_time}}
                            )
                            device_data['exit_time'] = current_time
                        device_data['active'] = False  # 4. Set the device as not active
                    else:
                        # 4. If the device is active and reappears in the current scan, update its entry time without deleting the previous entry time
                        if devices_in_range[mac_address]['exit_time'] == 0:
                            collection.update_one(
                                {"MAC_add": mac_address},
                                {"$push": {"Entry_time": current_time}}
                            )
                            devices_in_range[mac_address]['entry_time'] = current_time

        # 5. Update the list of devices from the previous scan
        previous_scan_devices = list(current_scan_devices)

        # You can print the data for testing purposes
        print("Scanned Devices -", current_scan_devices)
        print("Previous Devices -", previous_scan_devices)

# ...


# Flask route to get devices from the database
@app.route('/get_devices', methods=['GET'])
def get_devices():
    # Retrieve all devices from the database
    devices = list(collection.find({}, {"_id": 0}))
    return jsonify(devices)

if __name__ == "__main__":
    # Start the exit times update thread
    threading.Thread(target=update_exit_times).start()

    # Start the Flask app
    threading.Thread(target=app.run, kwargs={'port': 5000}).start()

    # Start the Bluetooth scanner
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(discover_devices())
