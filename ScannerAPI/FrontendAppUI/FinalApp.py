import os
import asyncio
from datetime import datetime
import tkinter as tk
from bleak import BleakScanner
import bluetooth
import threading
from pymongo import MongoClient
from dotenv import load_dotenv
import csv
import json
from tkinter import filedialog
from serial.tools.list_ports import comports
import time
import serial
import re

from flask import Flask, jsonify
from pymongo import MongoClient
from dotenv import load_dotenv
# Load environment variables from .env file
load_dotenv()

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
       
class MongoDBStorage:
    def __init__(self, mongodb_uri, db_name, collection_name, node_name, bluetooth_scanner_app):
        self.client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]
        self.node_name = node_name
        self.bluetooth_scanner_app = bluetooth_scanner_app  # Store the BluetoothScannerApp instance

    async def discover_devices(self):
        while True:
            bleak_devices = await self.scan_bleak_devices()
            pybluz_devices = self.scan_pybluz_devices()
            # nodemcu_devices = self.scan_nodemcu_devices()
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
            # devices.extend(nodemcu_devices)
            self.process_devices(devices)
            print(f"Scanned Devices - {len(devices)} devices")

    def process_devices(self, devices):
        mac_addresses = set()

        for device in devices:
            mac_address = device["MAC_add"]
            timestamp = device["Timestamp"]
            mac_addresses.add(mac_address)

            existing_device = self.collection.find_one({"MAC_add": mac_address})

            if existing_device:
                if self.node_name not in existing_device:
                    self.collection.update_one(
                        {"MAC_add": mac_address},
                        {"$set": {self.node_name: [timestamp]}}
                    )
                else:
                    self.collection.update_one(
                        {"MAC_add": mac_address},
                        {"$push": {self.node_name: timestamp}}
                    )
            else:
                new_device = {
                    "MAC_add": mac_address,
                    self.node_name: [timestamp]
                }
                self.collection.insert_one(new_device)

            real_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.bluetooth_scanner_app.update_tk_output(devices)
            print(f"Scanned Device - MAC: {mac_address}, Timestamp: {timestamp}, Real Time: {real_time}")

    async def scan_bleak_devices(self):
        return await BleakScanner.discover()

    def scan_pybluz_devices(self):
        return bluetooth.discover_devices(lookup_names=True)


class LocalStorage:
    def __init__(self, master, bluetooth_scanner_app):
        self.master = master
        self.bluetooth_scanner_app = bluetooth_scanner_app  # Store the BluetoothScannerApp instance
        self.folder_location = None
        
        self.tk_output_var = tk.StringVar()

    def store_locally(self):
        if self.folder_location is None:
            threading.Thread(target=self.choose_directory).start()
        else:
            self.master.after(0, self.process_directory, self.folder_location)

    def choose_directory(self):
        if self.folder_location is None:
            directory_path = filedialog.askdirectory(
                title="Select Directory to Save CSV and JSON Files"
            )
        self.master.after(0, self.process_directory, directory_path)

    def process_directory(self, directory_path):
        if not directory_path:
            return
        self.folder_location = directory_path
        self.save_folder_location()

        devices = self.scan_devices()

        csv_file_path = os.path.join(self.folder_location, "devices.csv")
        self.write_to_csv(devices, csv_file_path)

        json_file_path = os.path.join(self.folder_location, "devices.json")
        self.write_to_json(devices, json_file_path)

        real_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        print(f"Files saved at {self.folder_location} - CSV: {csv_file_path}, JSON: {json_file_path}, Real Time: {real_time}")
        
        for device in devices:
            mac_address = device["MAC_add"]
            timestamp = device["Timestamp"]
            real_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"Scanned Device - MAC: {mac_address}, Timestamp: {timestamp}, Real Time: {real_time}")        

        # Update the Tkinter UI with scanned devices
        self.bluetooth_scanner_app.update_tk_output(devices)
        self.master.after(500, self.store_locally)
         
    def scan_devices(self):
        bleak_devices = asyncio.run(self.scan_bleak_devices())
        pybluz_devices = self.scan_pybluz_devices()
        nodemcu_devices = scan_nodemcu_devices()
        
        
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
        devices.extend(nodemcu_devices)
        return devices

    async def scan_bleak_devices(self):
        return await BleakScanner.discover()

    def scan_pybluz_devices(self):
        return bluetooth.discover_devices(lookup_names=True)

    def write_to_csv(self, data, file_path):
        file_exists = os.path.exists(file_path)

        with open(file_path, 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=data[0].keys())

            if not file_exists:
                writer.writeheader()

            writer.writerows(data)

    def write_to_json(self, data, file_path):
        file_exists = os.path.exists(file_path)

        with open(file_path, 'a') as jsonfile:
            if not file_exists:
                jsonfile.write("[")

            if file_exists:
                jsonfile.seek(0, os.SEEK_END)
                file_size = jsonfile.tell()
                if file_size > 1:
                    jsonfile.seek(file_size - 1, os.SEEK_SET)
                    jsonfile.truncate()

            if file_exists and file_size > 1:
                jsonfile.write(",\n")

            json.dump(data, jsonfile)
            jsonfile.write("\n]")

    def save_folder_location(self):
        config_path = os.path.join(os.path.dirname(__file__), "config.txt")
        if not os.path.exists(config_path):
            with open(config_path, "w") as config_file:
                config_file.write(self.folder_location)

    def load_folder_location(self):
        config_path = os.path.join(os.path.dirname(__file__), "config.txt")
        if os.path.exists(config_path):
            with open(config_path, "r") as config_file:
                self.folder_location = config_file.read()
        else:
            self.folder_location = os.path.expanduser("~")


class BluetoothScannerApp:
    def __init__(self, master):
        self.master = master
        master.title("Bluetooth Device Scanner")

        self.mongodb_storage = None
        self.local_storage = None
        self.wifi_activated = False

        self.init_gui()

    def init_gui(self):
        self.master.geometry("500x650")  # Set initial window size
 
        self.mongodb_uri_label = tk.Label(self.master, text="MongoDB URI:")
        self.mongodb_uri_label.grid(row=0, column=0, padx=10, pady=5, sticky="e")

        self.mongodb_uri_entry = tk.Entry(self.master)
        self.mongodb_uri_entry.grid(row=0, column=1, padx=10, pady=5)

        self.db_name_label = tk.Label(self.master, text="Database Name:")
        self.db_name_label.grid(row=1, column=0, padx=10, pady=5, sticky="e")

        self.db_name_entry = tk.Entry(self.master)
        self.db_name_entry.grid(row=1, column=1, padx=10, pady=5)

        self.collection_name_label = tk.Label(self.master, text="Collection Name:")
        self.collection_name_label.grid(row=2, column=0, padx=10, pady=5, sticky="e")

        self.collection_name_entry = tk.Entry(self.master)
        self.collection_name_entry.grid(row=2, column=1, padx=10, pady=5)

        self.node_name_label = tk.Label(self.master, text="Node Name:")
        self.node_name_label.grid(row=3, column=0, padx=10, pady=5, sticky="e")

        self.node_name_entry = tk.Entry(self.master)
        self.node_name_entry.grid(row=3, column=1, padx=10, pady=5)

        self.store_option_var = tk.IntVar()
        self.store_option_var.set(2)  # Default: Store locally

        self.store_option_frame = tk.Frame(self.master)
        self.store_option_frame.grid(row=4, column=0, columnspan=2, pady=5)
        

        self.mongodb_radio_button = tk.Radiobutton(
            self.store_option_frame, text="Store in MongoDB",
            variable=self.store_option_var, value=1
        )
        self.mongodb_radio_button.grid(row=0, column=0, padx=5)

        self.local_csv_radio_button = tk.Radiobutton(
            self.store_option_frame, text="Store locally (CSV & JSON)",
            variable=self.store_option_var, value=2
        )
        self.local_csv_radio_button.grid(row=0, column=1, padx=5)
        
 
        self.folder_location = None
        self.load_folder_location()

        self.download_csv_button = tk.Button(self.master, text="Download Data", command=self.download_data)
        self.download_csv_button.grid(row=5, column=0, columnspan=2, pady=10)

        self.start_scanning_button = tk.Button(self.master, text="Start Scanning", command=self.start_scanning)
        self.start_scanning_button.grid(row=6, column=0, columnspan=2, pady=10)

        self.stop_scanning_button = tk.Button(self.master, text="Stop Scanning", command=self.stop_scanning)
        self.stop_scanning_button.grid(row=7, column=0, columnspan=2, pady=10)

        self.tk_output_var = tk.StringVar()
        self.tk_output = tk.Label(self.master, textvariable=self.tk_output_var, width=60, height=20)
        self.tk_output.grid(row=8, column=0, columnspan=2, padx=10, pady=10)
         

    def update_tk_output(self, devices):
        self.tk_output_var.set('')
        for device in devices:
            mac_address = device["MAC_add"]
            timestamp = datetime.fromtimestamp(device["Timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
            self.tk_output_var.set(f"{self.tk_output_var.get()}MAC: {mac_address}, Timestamp: {timestamp}\n")

    
    def start_scanning(self):
        store_option = self.store_option_var.get()

        if store_option == 1:  # Store in MongoDB
            self.mongodb_storage = MongoDBStorage(
                self.mongodb_uri_entry.get(),
                self.db_name_entry.get(),
                self.collection_name_entry.get(),
                self.node_name_entry.get(),
                self
            )
            threading.Thread(target=lambda: asyncio.run(self.mongodb_storage.discover_devices())).start()
        elif store_option == 2:  # Store locally in CSV
            self.local_storage = LocalStorage(self.master,self)
            
            threading.Thread(target=self.local_storage.store_locally).start()

    def stop_scanning(self):
        
        
        if self.mongodb_storage:
            # Stop MongoDB scanning
            self.mongodb_storage.client.close()
            self.mongodb_storage = None
        elif self.local_storage:
            # Stop local scanning
            self.local_storage.folder_location = None
            self.local_storage = None
             
    def download_data(self):
        store_option = self.store_option_var.get()

        if store_option == 1:  # Download from MongoDB
            if self.mongodb_storage:
                devices = list(self.mongodb_storage.collection.find({}, {"_id": 0}))
                file_path = filedialog.asksaveasfilename(
                    defaultextension=".json",
                    filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                    title="Save JSON file"
                )

                if file_path:  # User didn't cancel the dialog
                    with open(file_path, 'w') as jsonfile:
                        json.dump(devices, jsonfile)

        elif store_option == 2:  # Download from local CSV
            if self.local_storage:
                devices = self.local_storage.scan_devices()
                file_path = filedialog.asksaveasfilename(
                    defaultextension=".csv",
                    filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
                    title="Save CSV file"
                )

                if file_path:  # User didn't cancel the dialog
                    self.local_storage.write_to_csv(devices, file_path)


    def load_folder_location(self):
        if self.local_storage:
            self.local_storage.load_folder_location()

    def save_folder_location(self):
        if self.local_storage:
            self.local_storage.save_folder_location()


def main():
    root = tk.Tk()
    app = BluetoothScannerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
