import os
import asyncio
from datetime import datetime
from bleak import BleakScanner
from flask import Flask, jsonify
from pymongo import MongoClient
from dotenv import load_dotenv
import bluetooth
import threading
import csv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# MongoDB setup
mongodb_uri = os.getenv("MONGODB_URI")
client = MongoClient(mongodb_uri)
db = client["bluetooth"]
collection = db["ModifyData_march1"]
node_name = "TL road"
CSV_FILE_PATH = "device_data.csv"

def scan_pybluz_devices():
    return bluetooth.discover_devices(lookup_names=True)

async def scan_bleak_devices():
    return await BleakScanner.discover()

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

async def discover_devices():
    while True:
        bleak_devices = await BleakScanner.discover()
        pybluz_devices = bluetooth.discover_devices(lookup_names=True)
        
        devices = []
        for device in bleak_devices:
            devices.append({
                "MAC_add": device.address,
                "Timestamp": int(datetime.now().timestamp())
            })

        for addr, name in pybluz_devices:
            devices.append({
                "MAC_add": addr,
                "Timestamp": int(datetime.now().timestamp())
            })

        # Process and store devices in MongoDB
        process_devices(devices)

        # Print the data for testing purposes
        print(f"Scanned Devices - {len(devices)} devices")

        # await asyncio.sleep(60)  # Sleep for 60 seconds between scans

def process_devices(devices):
    for device in devices:
        mac_address = device["MAC_add"]
        timestamp = device["Timestamp"]

        existing_device = collection.find_one({"MAC_add": mac_address})

        if existing_device:
            # Check if the node_name field exists
            if node_name not in existing_device:
                # If not, create the field and initialize it with a list containing the timestamp
                collection.update_one(
                    {"MAC_add": mac_address},
                    {"$set": {node_name: [timestamp]}}
                )
            else:
                # If yes, append the timestamp to the existing list
                collection.update_one(
                    {"MAC_add": mac_address},
                    {"$push": {node_name: timestamp}}
                )
        else:
            new_device = {
                "MAC_add": mac_address,
                node_name: [timestamp]
            }
            collection.insert_one(new_device)
        real_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"Scanned Device - MAC: {mac_address}, Timestamp: {timestamp}, Real Time : {real_time}")
 
@app.route('/get_devices', methods=['GET'])
def get_devices():
    devices = list(collection.find({}, {"_id": 0}))
    return jsonify(devices)

if __name__ == "__main__":
    # Start Flask directly without threading
    threading.Thread(target=app.run, kwargs={'port': 5000}).start()

    # Start the Bluetooth scanner in the main thread
    asyncio.run(discover_devices())