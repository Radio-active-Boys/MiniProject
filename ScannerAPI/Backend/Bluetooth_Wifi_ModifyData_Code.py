import os
import asyncio
import time
from datetime import datetime

from bleak import BleakScanner
import bluetooth
import threading
import serial
import re
from serial.tools.list_ports import comports
import csv

from flask import Flask, jsonify
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

mongodb_uri = os.getenv("MONGODB_URI")
client = MongoClient(mongodb_uri)
db = client["bluetooth"]
collection = db["ModifyData_march16"]
node_name = "Room202_2"
csv_file_path = "device_data.csv"

def detect_com_port():
    ports = comports()
    for port in ports:
        if 'USB' in port.description:
            return port.device
    return None

def extract_mac_id(data):
    pattern = r'SRC: ([0-9A-Fa-f]{12})'
    match = re.search(pattern, data)
    if match:
        mac = match.group(1).upper()  # Convert to uppercase
        formatted_mac = ':'.join([mac[i:i + 2] for i in range(0, len(mac), 2)])
        return formatted_mac
    else:
        return None

def write_to_csv(data, device_type):
    if device_type != "NodeMCU":  # Exclude NodeMCU data
        with open(csv_file_path, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(data)

async def discover_devices():
    while True:
        try:
            # Record the start time
            start_time = time.time()

            devices = []

            # Discover BLE devices asynchronously
            bleak_devices = await BleakScanner.discover()
            for device in bleak_devices:
                devices.append({
                    "MAC_add": device.address,
                    "Timestamp": int(datetime.now().timestamp())
                })

            # Discover Bluetooth devices
            pybluz_devices = bluetooth.discover_devices(lookup_names=True)
            for addr, _ in pybluz_devices:
                devices.append({
                    "MAC_add": addr,
                    "Timestamp": int(datetime.now().timestamp())
                })

            # Discover NodeMCU devices
            nodemcu_devices = scan_nodemcu_devices()
            devices.extend(nodemcu_devices)

            # Process and store devices in MongoDB
            process_devices(devices)

            # Record the end time
            end_time = time.time()

            # Print the total time taken for the scan
            total_time = end_time - start_time
            print(f"Total time taken for scan: {total_time:.2f} seconds")

            # Print the data for testing purposes
            print(f"Scanned Devices - {len(devices)} devices")
        except Exception as e:
            print(f"Error in scanning devices: {e}")

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

def scan_nodemcu_devices():
    nodemcu_devices = []

    try:
        # Detect COM port
        com_port = detect_com_port()
        if com_port is None:
            print("COM port not found. Please Connect NodeMCU")
            return nodemcu_devices

        # Open serial connection
        ser = serial.Serial(com_port, baudrate=115200, timeout=1)

        # Read data from serial port
        start_time = time.time()
        while time.time() - start_time < 5:  # Collect data for 5 seconds
            try:
                data = ser.readline().decode('utf-8', errors='ignore').strip()  # Read a line from serial
                mac_id = extract_mac_id(data)
                if mac_id:
                    nodemcu_devices.append({
                        "MAC_add": mac_id,
                        "Timestamp": int(datetime.now().timestamp())
                    })
            except KeyboardInterrupt:
                print("Stopping...")
                break

        # Close serial connection
        ser.close()
    except serial.SerialException:
        print("Failed to open serial port. Retrying...")
    except Exception as e:
        print(f"Error in NodeMCU scanning: {e}")

    return nodemcu_devices

@app.route('/get_devices', methods=['GET'])
def get_devices():
    devices = list(collection.find({}, {"_id": 0}))
    return jsonify(devices)

if __name__ == "__main__":
    # Start Flask directly without threading
    flask_thread = threading.Thread(target=app.run, kwargs={'port': 5000})
    flask_thread.start()

    # Start device discovery
    loop = asyncio.get_event_loop()
    loop.run_until_complete(discover_devices())
