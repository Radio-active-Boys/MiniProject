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

# Load environment variables from .env file
load_dotenv()

# Tkinter GUI
class BluetoothScannerApp:
    def __init__(self, master):
        self.master = master
        master.title("Bluetooth Device Scanner")

        self.collection = None
        self.after_id = None  # To store the ID returned by after() method

        self.mongodb_uri_label = tk.Label(master, text="MongoDB URI:")
        self.mongodb_uri_label.grid(row=0, column=0, padx=10, pady=5, sticky="e")

        self.mongodb_uri_entry = tk.Entry(master)
        self.mongodb_uri_entry.grid(row=0, column=1, padx=10, pady=5)

        self.db_name_label = tk.Label(master, text="Database Name:")
        self.db_name_label.grid(row=1, column=0, padx=10, pady=5, sticky="e")

        self.db_name_entry = tk.Entry(master)
        self.db_name_entry.grid(row=1, column=1, padx=10, pady=5)

        self.collection_name_label = tk.Label(master, text="Collection Name:")
        self.collection_name_label.grid(row=2, column=0, padx=10, pady=5, sticky="e")

        self.collection_name_entry = tk.Entry(master)
        self.collection_name_entry.grid(row=2, column=1, padx=10, pady=5)

        self.node_name_label = tk.Label(master, text="Node Name:")
        self.node_name_label.grid(row=3, column=0, padx=10, pady=5, sticky="e")

        self.node_name_entry = tk.Entry(master)
        self.node_name_entry.grid(row=3, column=1, padx=10, pady=5)

        self.store_option_var = tk.IntVar()
        self.store_option_var.set(2)  # Default: Store in Locally

        self.store_option_frame = tk.Frame(master)
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

        self.download_csv_button = tk.Button(master, text="Download Data", command=self.download_data)
        self.download_csv_button.grid(row=5, column=0, columnspan=2, pady=10)

        self.start_scanning_button = tk.Button(master, text="Start Scanning", command=self.start_scanning)
        self.start_scanning_button.grid(row=6, column=0, columnspan=2, pady=10)

        # Stop Scanning button
        self.stop_scanning_button = tk.Button(master, text="Stop Scanning", command=self.stop_scanning)
        self.stop_scanning_button.grid(row=7, column=0, columnspan=2, pady=10)

        self.tk_output_var = tk.StringVar()
        self.tk_output = tk.Label(master, textvariable=self.tk_output_var, width=60, height=20)
        self.tk_output.grid(row=8, column=0, columnspan=2, padx=10, pady=10)

    def start_scanning(self):
        store_option = self.store_option_var.get()

        if store_option == 1:  # Store in MongoDB
            self.store_in_mongodb()
        elif store_option == 2:  # Store locally in CSV
            self.store_locally()

    def store_in_mongodb(self):
        mongodb_uri = self.mongodb_uri_entry.get()
        db_name = self.db_name_entry.get()
        collection_name = self.collection_name_entry.get()
        node_name = self.node_name_entry.get()

        # MongoDB setup
        client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5)
        db = client[db_name]
        self.collection = db[collection_name]

        async def discover_devices():
            while True:
                bleak_devices = await self.scan_bleak_devices()
                pybluz_devices = self.scan_pybluz_devices()

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

                self.process_devices(devices, self.collection, node_name)
                print(f"Scanned Devices - {len(devices)} devices")

        threading.Thread(target=lambda: asyncio.run(discover_devices())).start()

        # Schedule the start_scanning method to run every 1000 milliseconds (1 second)
        self.after_id = self.master.after(1000, self.start_scanning)

    def store_locally(self):
        if self.folder_location is None:
            # Use a separate thread for directory selection
            threading.Thread(target=self.choose_directory).start()
        else:
            # Use the pre-existing folder location
            self.master.after(0, self.process_directory, self.folder_location)

    def choose_directory(self):
        if self.folder_location is None:
            directory_path = filedialog.askdirectory(
                title="Select Directory to Save CSV and JSON Files"
            )     
 
        # After the user selects the directory, continue with processing in the main thread
        self.master.after(0, self.process_directory, directory_path)

    def process_directory(self, directory_path):
        if not directory_path:  # User canceled the dialog
            return

        self.folder_location = directory_path
        self.save_folder_location()

        # Continue with the rest of the processing
        devices = self.scan_devices()

        # Create CSV file
        csv_file_path = os.path.join(self.folder_location, "devices.csv")
        self.write_to_csv(devices, csv_file_path)

        # Create JSON file
        json_file_path = os.path.join(self.folder_location, "devices.json")
        self.write_to_json(devices, json_file_path)

        real_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"Files saved at {self.folder_location} - CSV: {csv_file_path}, JSON: {json_file_path}, Real Time: {real_time}")

        # Schedule the start_scanning method to run every 1000 milliseconds (1 second)
        self.after_id = self.master.after(1000, self.start_scanning)

    def stop_scanning(self):
        # Clear the folder location when scanning is stopped
        self.folder_location = None

        # Cancel the scheduled scanning
        if self.after_id:
            self.master.after_cancel(self.after_id)
            self.after_id = None

    def scan_pybluz_devices(self):
        return bluetooth.discover_devices(lookup_names=True)

    async def scan_bleak_devices(self):
        return await BleakScanner.discover()

    def scan_devices(self):
        bleak_devices = asyncio.run(self.scan_bleak_devices())
        pybluz_devices = self.scan_pybluz_devices()

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

        return devices

    def write_to_csv(self, data, file_path):
        # Check if the file exists
        file_exists = os.path.exists(file_path)

        with open(file_path, 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=data[0].keys())

            # Write the header only if the file is newly created
            if not file_exists:
                writer.writeheader()

            writer.writerows(data)

    def write_to_json(self, data, file_path):
        # Check if the file exists
        file_exists = os.path.exists(file_path)

        with open(file_path, 'a') as jsonfile:
            if not file_exists:
                jsonfile.write("[")  # Start JSON array if the file is newly created

            if file_exists:
                jsonfile.seek(0, os.SEEK_END)
                file_size = jsonfile.tell()
                if file_size > 1:
                    jsonfile.seek(file_size - 1, os.SEEK_SET)
                    jsonfile.truncate()  # Remove the trailing ']' to append new data

            # Write data in JSON format
            if file_exists and file_size > 1:
                jsonfile.write(",\n")

            json.dump(data, jsonfile)

            # Add a comma and newline to separate arrays in JSON array
            jsonfile.write("\n]")

    def process_devices(self, devices, collection, node_name):
        mac_addresses = set()  # To keep track of unique MAC addresses

        for device in devices:
            mac_address = device["MAC_add"]
            timestamp = device["Timestamp"]
            mac_addresses.add(mac_address)

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
            print(f"Scanned Device - MAC: {mac_address}, Timestamp: {timestamp}, Real Time: {real_time}")

        # Update the Tkinter UI with scanned devices
        self.update_tk_output(devices)

        # Print the aggregated information in the desired format
        for mac_address in mac_addresses:
            existing_device = collection.find_one({"MAC_add": mac_address})
            if existing_device:
                timestamps = existing_device.get(node_name, [])
                print(f"{mac_address},{','.join(map(str, timestamps))}")

    def update_tk_output(self, devices):
        self.tk_output_var.set('')
        for device in devices:
            mac_address = device["MAC_add"]
            timestamp = datetime.fromtimestamp(device["Timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
            self.tk_output_var.set(f"{self.tk_output_var.get()}MAC: {mac_address}, Timestamp: {timestamp}\n")

    def download_data(self):
        store_option = self.store_option_var.get()

        # Stop continuous scanning when downloading
        self.stop_scanning()

        if store_option == 1:  # Download from MongoDB
            self.download_from_mongodb()
        elif store_option == 2:  # Download from local CSV
            self.download_from_csv()

    def download_from_mongodb(self):
        devices = list(self.collection.find({}, {"_id": 0}))
        file_path = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            title="Save JSON file"
        )

        if not file_path:  # User canceled the dialog
            return

        with open(file_path, 'w') as jsonfile:
            json.dump(devices, jsonfile)

        # Resume continuous scanning after downloading
        self.after_id = self.master.after(1000, self.start_scanning)

    def download_from_csv(self):
        devices = self.scan_devices()
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Save CSV file"
        )

        if not file_path:  # User canceled the dialog
            return

        self.write_to_csv(devices, file_path)

        # Resume continuous scanning after downloading
        self.after_id = self.master.after(1000, self.start_scanning)

    def save_folder_location(self):
        # Save the folder location to a configuration file only if it hasn't been saved before
        config_path = os.path.join(os.path.dirname(__file__), "config.txt")
        if not os.path.exists(config_path):
            with open(config_path, "w") as config_file:
                config_file.write(self.folder_location)

    def load_folder_location(self):
        # Load the folder location from the configuration file
        config_path = os.path.join(os.path.dirname(__file__), "config.txt")
        if os.path.exists(config_path):
            with open(config_path, "r") as config_file:
                self.folder_location = config_file.read()
        else:
            # Set a default folder location if the configuration file doesn't exist
            self.folder_location = os.path.expanduser("~") 

def main():
    root = tk.Tk()
    app = BluetoothScannerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
