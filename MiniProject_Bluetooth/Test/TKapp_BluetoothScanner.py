import os
import asyncio
import csv
import tkinter as tk
from tkinter import ttk
from bleak import BleakScanner

class BluetoothScannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Bluetooth Device Scanner")

        self.devices_data = []
        self.scanning = False

        self.create_widgets()

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

    async def discover_devices(self):
        while self.scanning:
            devices = await BleakScanner.discover()
            devices.sort(key=lambda device: device.rssi, reverse=True)

            self.devices_data = [(device.name if device.name else device.address, device.address, device.rssi, device.details) for device in devices]

            self.update_treeview()
            await asyncio.sleep(1)

    def update_treeview(self):
        self.tree.delete(*self.tree.get_children())

        for device_data in self.devices_data:
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

    def export_to_csv(self):
        with open('discovered_devices.csv', 'w', newline='') as csvfile:
            fieldnames = ['Device Name', 'Device Address', 'RSSI', 'Details']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for device_data in self.devices_data:
                writer.writerow({'Device Name': device_data[0], 'Device Address': device_data[1], 'RSSI': device_data[2], 'Details': device_data[3]})

if __name__ == "__main__":
    root = tk.Tk()
    app = BluetoothScannerApp(root)
    root.mainloop()
