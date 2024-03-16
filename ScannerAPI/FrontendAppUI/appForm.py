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
from tkinter import filedialog
# Load environment variables from .env file
load_dotenv()

# Tkinter GUI
class BluetoothScannerApp:
    def __init__(self, master):
        self.master = master
        master.title("Bluetooth Device Scanner")
        
        self.collection = None

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

        self.download_csv_button = tk.Button(master, text="Download CSV", command=self.download_csv)
        self.download_csv_button.grid(row=5, column=0, columnspan=2, pady=10)

        self.start_scanning_button = tk.Button(master, text="Start Scanning", command=self.start_scanning)
        self.start_scanning_button.grid(row=6, column=0, columnspan=2, pady=10)

        self.tk_output_var = tk.StringVar()
        self.tk_output = tk.Label(master, textvariable=self.tk_output_var, width=60, height=20)
        self.tk_output.grid(row=7, column=0, columnspan=2, padx=10, pady=10)

    def start_scanning(self):
        mongodb_uri = self.mongodb_uri_entry.get()
        db_name = self.db_name_entry.get()
        collection_name = self.collection_name_entry.get()
        node_name = self.node_name_entry.get()
         

        # MongoDB setup
        client = MongoClient(mongodb_uri, serverSelectionTimeoutMS=5)
        db = client[db_name]
        self.collection  = db[collection_name]

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
                self.update_tk_output(devices)

                print(f"Scanned Devices - {len(devices)} devices")

                 

        threading.Thread(target=lambda: asyncio.run(discover_devices())).start()

    def scan_pybluz_devices(self):
        return bluetooth.discover_devices(lookup_names=True)

    async def scan_bleak_devices(self):
        return await BleakScanner.discover()

    def write_to_csv(self, data):
        with open(self.csv_file_path_entry.get(), 'a', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(data)

    def process_devices(self, devices, collection, node_name):
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
            print(f"Scanned Device - MAC: {mac_address}, Timestamp: {timestamp}, Real Time : {real_time}")

    def update_tk_output(self, devices):
        self.tk_output_var.set('')
        for device in devices:
            mac_address = device["MAC_add"]
            timestamp = datetime.fromtimestamp(device["Timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
            self.tk_output_var.set(f"{self.tk_output_var.get()}MAC: {mac_address}, Timestamp: {timestamp}\n")

    def download_csv(self):
        devices = list(self.collection.find({}, {"_id": 0}))
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Save CSV file"
        )

        if not file_path:  # User canceled the dialog
            return

        with open(file_path, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=devices[0].keys())
            writer.writeheader()
            writer.writerows(devices)


def main():
    root = tk.Tk()
    app = BluetoothScannerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
