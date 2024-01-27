import os
import asyncio
import keyboard
from datetime import datetime
from bleak import BleakScanner
from flask import Flask, request, jsonify
from pymongo import MongoClient

app = Flask(__name__)

# MongoDB setup
client = MongoClient("mongodb+srv://iitjammu7:W95nUBv78dUKI6si@cluster1.0pamvyh.mongodb.net/?retryWrites=true&w=majority")
db = client["bluetooth"]
collection = db["test1"]

async def discover_devices():
    while not keyboard.is_pressed('q'):
        devices = await BleakScanner.discover()
        
        for device in devices:
            mac_address = device.address
            timestamp = int(datetime.now().timestamp())

            # Check if the device is already in the database
            existing_device = collection.find_one({"MAC_add": mac_address})

            if existing_device:
                # If the device exists, update its timestamp array
                existing_device["Unix_TimeStamp"].append(timestamp)
                collection.update_one({"_id": existing_device["_id"]}, {"$set": existing_device})
            else:
                # If the device does not exist, insert a new document
                new_device = {
                    "MAC_add": mac_address,
                    "Unix_TimeStamp": [timestamp]
                }
                collection.insert_one(new_device)

            # You can print the data for testing purposes
            print(f"Scanned Device - MAC: {mac_address}, Timestamp: {timestamp}")

@ app.route('/get_devices', methods=['GET'])
def get_devices():
    # Retrieve all devices from the database
    devices = list(collection.find({}, {"_id": 0}))

    return jsonify(devices)

if __name__ == "__main__":
    # Start the Flask app in a separate thread
    import threading
    threading.Thread(target=app.run, kwargs={'port': 5000}).start()

    # Start the Bluetooth scanner in the main thread
    asyncio.run(discover_devices())
