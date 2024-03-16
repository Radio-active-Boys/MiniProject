import os
import asyncio
import time
from datetime import datetime
from bleak import BleakScanner
from flask import Flask, jsonify
from pymongo import MongoClient
from dotenv import load_dotenv
import bluetooth
import threading
import csv
import serial
import re
from serial.tools import list_ports

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

def detect_com_port():
    ports = list_ports.comports()
    for port in ports:
        if 'USB' in port.description:
            return port.device
    return None

def extract_mac_id(data):
    # Extract MAC address from SRC field
    pattern = r'SRC: ([0-9A-Fa-f]{12})'
    match = re.search(pattern, data)
    if match:
        mac = match.group(1)
        # Format MAC address as XX:XX:XX:XX:XX:XX
        formatted_mac = ':'.join([mac[i:i+2] for i in range(0, len(mac), 2)])
        return formatted_mac
    else:
        return None

def write_to_csv(data, device_type):
    if device_type != "NodeMCU":  # Exclude NodeMCU data
        with open(CSV_FILE_PATH, 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(data)

def scan_pybluz_devices():
    return bluetooth.discover_devices(lookup_names=True)

async def scan_bleak_devices():
    return await BleakScanner.discover()

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

        write_to_csv([datetime.now().strftime("%Y-%m-%d %H:%M:%S"), device_name, device_address, existing_devices[device_name]], "Bluetooth")

    return existing_devices

async def discover_devices():
    while True:
        try:
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
    while True:
        try:
            # Detect COM port
            com_port = detect_com_port()
            if com_port is None:
                print("COM port not found. Retrying...")
                continue

            # Open serial connection
            ser = serial.Serial(com_port, baudrate=115200, timeout=1)

            # Read data from serial port and write to CSV
            while True:
                try:
                    data = ser.readline().decode('utf-8', errors='ignore').strip()  # Read a line from serial
                    mac_id = extract_mac_id(data)
                except KeyboardInterrupt:
                    print("Stopping...")
                    break

            # Close serial connection
            ser.close()
        except serial.SerialException:
            print("Failed to open serial port. Retrying...")
        except Exception as e:
            print(f"Error in NodeMCU scanning: {e}")

        # Add a delay to prevent continuous looping
        time.sleep(1)

# Feature toggle for each scanning method
pybluz_active = True
bleak_active = True
nodemcu_active = True

@app.route('/get_devices', methods=['GET'])
def get_devices():
    devices = list(collection.find({}, {"_id": 0}))
    return jsonify(devices)

if __name__ == "__main__":
    # Start Flask directly without threading
    flask_thread = threading.Thread(target=app.run, kwargs={'port': 5000})
    flask_thread.start()

    # Start the Bluetooth scanner in a separate thread if active
    if bleak_active:
        asyncio.run(discover_devices())

    # Start the NodeMCU scanner in a separate thread if active
    if nodemcu_active:
        scan_nodemcu_devices()
