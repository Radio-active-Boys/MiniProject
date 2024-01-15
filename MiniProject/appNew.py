import os
import asyncio
import csv
import tkinter as tk
from tkinter import ttk
from bleak import BleakScanner
from datetime import datetime

class BluetoothScannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bluetooth Device Scanner")

        self.devices_data = []
        self.unique_devices = {}  # Dictionary to store unique devices and their discovery time
        self.scanning = False

        # Create directories for CSV files
        self.export_directory = "List_Active_Devices"
        self.download_directory = "List_All_Devices"
        self.create_directories()

        self.create_widgets()

    def create_directories(self):
        os.makedirs(self.export_directory, exist_ok=True)
        os.makedirs(self.download_directory, exist_ok=True)

    def create_widgets(self):
        self.label = ttk.Label(self.root, text="Discovered devices:")
        self.label.pack(pady=10)

        self.tree = ttk.Treeview(self.root, columns=("Device Name", "Device Address", "RSSI", "Details"), show="headings")

        self.tree.heading("Device Name", text="Device Name")
        self.tree.heading("Device Address", text="Device Address")
        self.tree.heading("RSSI", text="RSSI")
        self.tree.heading("Details", text="Details")

        self.tree.pack(expand=True, fill="both")

        self.start_button = ttk.Button(self.root, text="Start Scanning", command=self.start_scanning)
        self.start_button.pack(pady=10)

        self.stop_button = ttk.Button(self.root, text="Stop Scanning", command=self.stop_scanning, state=tk.DISABLED)
        self.stop_button.pack(pady=10)

        self.export_button = ttk.Button(self.root, text="Export to CSV", command=self.export_to_csv)
        self.export_button.pack(pady=10)

        self.download_list_button = ttk.Button(self.root, text="Download List", command=self.download_unique_device_list)
        self.download_list_button.pack(pady=10)

    async def discover_devices(self):
        while self.scanning:
            devices = await BleakScanner.discover()
            devices.sort(key=lambda device: device.rssi, reverse=True)

            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            for device in devices:
                device_address = device.address
                if device_address not in self.unique_devices:
                    device_info = (
                        device.name if device.name else device_address,
                        device_address,
                        device.rssi,
                        device.details,
                        current_time
                    )
                    self.unique_devices[device_address] = device_info

            self.devices_data = list(self.unique_devices.values())
            self.update_treeview()
            await asyncio.sleep(1)

    def update_treeview(self):
        active_devices = [device for device in self.devices_data if self.is_active(device[4])]
        self.tree.delete(*self.tree.get_children())

        for device_data in active_devices:
            self.tree.insert("", "end", values=device_data)

    def is_active(self, discovery_time):
        current_time = datetime.now()
        discovery_datetime = datetime.strptime(discovery_time, "%Y-%m-%d %H:%M:%S")
        time_difference = current_time - discovery_datetime
        return time_difference.total_seconds() < 10

    def start_scanning(self):
        self.scanning = True
        self.start_button["state"] = tk.DISABLED
        self.stop_button["state"] = tk.NORMAL

        loop = asyncio.get_event_loop()
        loop.create_task(self.discover_devices())

        self.root.after(100, self.check_asyncio_tasks)

    def stop_scanning(self):
        self.scanning = False
        self.start_button["state"] = tk.NORMAL
        self.stop_button["state"] = tk.DISABLED

    def check_asyncio_tasks(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.sleep(0.1))
        self.root.after(100, self.check_asyncio_tasks)

    def export_to_csv(self):
        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = os.path.join(self.export_directory, f'discovered_devices_{current_time}.csv')
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = ['Device Name', 'Device Address', 'RSSI', 'Details']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for device_data in self.devices_data:
                writer.writerow({'Device Name': device_data[0], 'Device Address': device_data[1], 'RSSI': device_data[2], 'Details': device_data[3]})

    def download_unique_device_list(self):
        filename = os.path.join(self.download_directory, 'unique_devices_list.csv')
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = ['Device Name', 'Device Address', 'RSSI', 'Details', 'Discovery Time']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for device_data in self.unique_devices.values():
                writer.writerow({'Device Name': device_data[0], 'Device Address': device_data[1], 'RSSI': device_data[2], 'Discovery Time': device_data[4]})

if __name__ == "__main__":
    root = tk.Tk()
    app = BluetoothScannerApp(root)
    root.mainloop()
