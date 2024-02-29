import os
import asyncio
import csv
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from bleak import BleakScanner, BleakError
import bluetooth
import time

class BluetoothScannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bluetooth Device Scanner")

        self.devices_data = []
        self.unique_devices = {}  # Dictionary to store unique devices and their discovery time
        self.scanning_bleak = False
        self.scanning_bluetooth = False
        self.scannedDevices_bleak = []
        self.scannedDevices_bluetooth = []
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

        self.tree = ttk.Treeview(self.root, columns=("Device Name", "Device Address"), show="headings")

        self.tree.heading("Device Name", text="Device Name")
        self.tree.heading("Device Address", text="Device Address")

        self.tree.pack(expand=True, fill="both")

        self.start_button = ttk.Button(self.root, text="Start Scanning", command=self.start_scanning)
        self.start_button.pack(pady=10)

        self.stop_button = ttk.Button(self.root, text="Stop Scanning", command=self.stop_scanning, state=tk.DISABLED)
        self.stop_button.pack(pady=10)

        self.export_button = ttk.Button(self.root, text="Export to CSV", command=self.export_to_csv)
        self.export_button.pack(pady=10)

        self.download_list_button = ttk.Button(self.root, text="Download List", command=self.download_unique_device_list)
        self.download_list_button.pack(pady=10)

    async def discover_devices_bleak(self):
        while self.scanning_bleak:
            try:
                devices = await BleakScanner.discover()
                self.scannedDevices_bleak = devices
                current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                for device in devices:
                    device_address = device.address
                    if device_address not in self.unique_devices:
                        device_info = (
                            device.name , # if device.name else device_address
                            device_address,
                            current_time
                        )
                        self.unique_devices[device_address] = device_info

                self.devices_data = list(self.unique_devices.values())
                self.update_treeview()
            except BleakError as e:
                print(f"BleakError: {e}")

            await asyncio.sleep(1)

    def discover_devices_bluetooth(self):
        while self.scanning_bluetooth:
            nearby_devices = bluetooth.discover_devices(lookup_names=True)
            self.scannedDevices_bluetooth = nearby_devices
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            for addr, name in nearby_devices:
                device_address = addr
                if device_address not in self.unique_devices:
                    device_info = (
                        name,  # if name else device_address
                        device_address,
                        current_time
                    )
                    self.unique_devices[device_address] = device_info

            self.devices_data = list(self.unique_devices.values())
            self.update_treeview()
            time.sleep(1)  # Bluetooth scan interval (adjust as needed)


    def is_active(self, id):
        for device in self.scannedDevices_bleak + self.scannedDevices_bluetooth:
            if isinstance(device, tuple) and device[1] == id:
                return True
            elif hasattr(device, 'address') and device.address == id:
                return True
        return False

    def update_treeview(self):
        self.tree.delete(*self.tree.get_children())

        for device_data in self.devices_data:
            if self.is_active(device_data[1]):
                self.tree.insert("", "end", values=device_data)



    def start_scanning(self):
        self.scanning_bleak = True
        self.scanning_bluetooth = True
        self.start_button["state"] = tk.DISABLED
        self.stop_button["state"] = tk.NORMAL

        loop = asyncio.get_event_loop()
        loop.create_task(self.discover_devices_bleak())
        loop.run_in_executor(None, self.discover_devices_bluetooth)

        self.root.after(100, self.check_asyncio_tasks)

    def stop_scanning(self):
        self.scanning_bleak = False
        self.scanning_bluetooth = False
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
            fieldnames = ['Device Name', 'Device Address']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for device_data in self.devices_data:
                writer.writerow({'Device Name': device_data[0], 'Device Address': device_data[1] })

    def download_unique_device_list(self):
        filename = os.path.join(self.download_directory, 'unique_devices_list.csv')
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = ['Device Name', 'Device Address', 'Discovery Time']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for device_data in self.unique_devices.values():
                writer.writerow({'Device Name': device_data[0], 'Device Address': device_data[1],  'Discovery Time': device_data[2]})

if __name__ == "__main__":
    root = tk.Tk()
    app = BluetoothScannerApp(root)
    root.mainloop()
