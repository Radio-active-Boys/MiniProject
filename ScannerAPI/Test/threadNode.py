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

def discover_ble_devices():
    while True:
        try:
            devices = []
            bleak_devices = asyncio.run(BleakScanner.discover())
            for device in bleak_devices:
                devices.append({
                    "MAC_add": device.address,
                    "Timestamp": int(datetime.now().timestamp())
                })
            process_devices(devices, "BLE")
        except Exception as e:
            print(f"Error in BLE scanning: {e}")

def discover_pybluz_devices():
    while True:
        try:
            devices = []
            pybluz_devices = bluetooth.discover_devices(lookup_names=True)
            for addr, _ in pybluz_devices:
                devices.append({
                    "MAC_add": addr,
                    "Timestamp": int(datetime.now().timestamp())
                })
            process_devices(devices, "PyBluz")
        except Exception as e:
            print(f"Error in PyBluz scanning: {e}")

def discover_nodemcu_devices():
    while True:
        try:
            nodemcu_devices = []
            com_port = detect_com_port()
            if com_port is None:
                print("COM port not found. Retrying...")
                continue

            ser = serial.Serial(com_port, baudrate=115200, timeout=1)

            start_time = time.time()
            while time.time() - start_time < 5:
                try:
                    data = ser.readline().decode('utf-8', errors='ignore').strip()
                    mac_id = extract_mac_id(data)
                    if mac_id:
                        nodemcu_devices.append({
                            "MAC_add": mac_id,
                            "Timestamp": int(datetime.now().timestamp())
                        })
                except KeyboardInterrupt:
                    print("Stopping...")
                    break

            ser.close()
            process_devices(nodemcu_devices, "NodeMCU")
        except serial.SerialException:
            print("Failed to open serial port. Retrying...")
        except Exception as e:
            print(f"Error in NodeMCU scanning: {e}")

def process_devices(devices, device_type):
    for device in devices:
        mac_address = device["MAC_add"]
        timestamp = device["Timestamp"]

        existing_device = collection.find_one({"MAC_add": mac_address})

        if existing_device:
            if node_name not in existing_device:
                collection.update_one(
                    {"MAC_add": mac_address},
                    {"$set": {node_name: [timestamp]}}
                )
            else:
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
        print(f"Scanned Device - MAC: {mac_address}, Timestamp: {timestamp}, Real Time : {real_time}, Device Type: {device_type}")

@app.route('/get_devices', methods=['GET'])
def get_devices():
    devices = list(collection.find({}, {"_id": 0}))
    return jsonify(devices)

if __name__ == "__main__":
    # Start Flask directly without threading
    flask_thread = threading.Thread(target=app.run, kwargs={'port': 5000})
    flask_thread.start()

    # Start BLE device discovery
    ble_thread = threading.Thread(target=discover_ble_devices)
    ble_thread.start()

    # Start PyBluz device discovery
    pybluz_thread = threading.Thread(target=discover_pybluz_devices)
    pybluz_thread.start()

    # Start NodeMCU device discovery
    nodemcu_thread = threading.Thread(target=discover_nodemcu_devices)
    nodemcu_thread.start()