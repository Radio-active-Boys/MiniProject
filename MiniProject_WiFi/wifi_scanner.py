import os
import re
import asyncio
import json
import csv
import tkinter as tk
from tkinter import ttk
from datetime import datetime

class WiFiScannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("WiFi Network Scanner")

        self.all_devices_data = {}
        self.live_devices_data = set()
        self.scanning = False

        # Define the directory names
        self.base_directory = "Wifi_Scanner_Data"
        self.all_devices_directory = os.path.join(self.base_directory, "All_Devices")
        self.live_devices_directory = os.path.join(self.base_directory, "Live_Devices")

        self.create_widgets()

    def create_widgets(self):
        self.label = ttk.Label(self.root, text="WiFi devices:")
        self.label.pack(pady=10)

        self.tree = ttk.Treeview(self.root, columns=("Name", "MAC Address", "Type", "Connected Time"), show="headings")
        self.tree.heading("Name", text="Device Name")
        self.tree.heading("MAC Address", text="MAC Address")
        self.tree.heading("Type", text="Type")
        self.tree.heading("Connected Time", text="Connected Time")
        self.tree.pack(expand=True, fill="both")

        self.start_button = ttk.Button(self.root, text="Start Scanning", command=self.start_scanning)
        self.start_button.pack(pady=10)

        self.stop_button = ttk.Button(self.root, text="Stop Scanning", command=self.stop_scanning, state=tk.DISABLED)
        self.stop_button.pack(pady=10)

        self.export_all_button_csv = ttk.Button(self.root, text="Export All to CSV", command=self.export_all_to_csv)
        self.export_all_button_csv.pack(pady=10)

        self.export_live_button_csv = ttk.Button(self.root, text="Export Live to CSV", command=self.export_live_to_csv)
        self.export_live_button_csv.pack(pady=10)

        self.export_button_json = ttk.Button(self.root, text="Export to JSON", command=self.export_to_json)
        self.export_button_json.pack(pady=10)

    async def discover_devices(self):
        while self.scanning:
            # Run the command to list connected and available devices
            result = os.popen("arp -a").read()
            devices = [line.strip() for line in result.split('\n') if line.strip()]

            # Parse the device information using regular expression
            pattern = re.compile(r'(?P<IP>\d+\.\d+\.\d+\.\d+)\s+(?P<MAC>[0-9a-fA-F-]+)\s+(?P<Type>dynamic|static)')
            matches = [pattern.match(device) for device in devices]

            # Extract relevant information and update treeview with timestamp
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            all_devices = [(match.group('IP'), match.group('MAC'), match.group('Type'), current_time) for match in matches if match]
            for device_data in all_devices:
                mac_address = device_data[1]
                self.all_devices_data[mac_address] = device_data  # Use MAC address as the key
                self.live_devices_data.add(mac_address)

            self.update_treeview()
            await asyncio.sleep(1)

    def update_treeview(self):
        self.tree.delete(*self.tree.get_children())

        for device_data in self.all_devices_data.values():
            self.tree.insert("", "end", values=device_data)

    def start_scanning(self):
        self.scanning = True
        self.start_button["state"] = tk.DISABLED
        self.stop_button["state"] = tk.NORMAL

        # Run the discover_devices coroutine in the asyncio event loop
        loop = asyncio.get_event_loop()
        loop.create_task(self.discover_devices())

        # Update the Tkinter event loop to process asyncio tasks
        self.root.after(100, self.check_asyncio_tasks)

    def stop_scanning(self):
        self.scanning = False
        self.start_button["state"] = tk.NORMAL
        self.stop_button["state"] = tk.DISABLED

    def check_asyncio_tasks(self):
        # This function ensures that asyncio tasks are processed in the Tkinter event loop
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.sleep(0.1))
        self.root.after(100, self.check_asyncio_tasks)

    def create_directories(self):
        # Create the base directory if it does not exist
        if not os.path.exists(self.base_directory):
            os.makedirs(self.base_directory)

        # Create the 'all_devices' directory if it does not exist
        if not os.path.exists(self.all_devices_directory):
            os.makedirs(self.all_devices_directory)

        # Create the 'live_devices' directory if it does not exist
        if not os.path.exists(self.live_devices_directory):
            os.makedirs(self.live_devices_directory)

    def export_all_to_csv(self):
        self.create_directories()
        filename = os.path.join(self.all_devices_directory, 'all_devices.csv')
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = ["Name", "MAC Address", "Type", "Connected Time"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for device_data in self.all_devices_data.values():
                writer.writerow({field: device_data[i] for i, field in enumerate(fieldnames)})

    def export_live_to_csv(self):
        self.create_directories()
        current_time_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(self.live_devices_directory, f'live_devices_{current_time_str}.csv')
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = ["Name", "MAC Address", "Type", "Connected Time"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for mac_address in self.live_devices_data:
                writer.writerow({field: self.all_devices_data[mac_address][i] for i, field in enumerate(fieldnames)})

    def export_to_json(self):
        self.create_directories()
        filename = os.path.join(self.all_devices_directory, 'all_devices.json')
        with open(filename, 'w') as jsonfile:
            data = list(self.all_devices_data.values())
            json.dump(data, jsonfile, indent=2)

if __name__ == "__main__":
    root = tk.Tk()
    app = WiFiScannerApp(root)
    root.mainloop()
