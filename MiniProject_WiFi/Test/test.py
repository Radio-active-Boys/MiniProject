import os
import json
import csv
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from scapy.all import ARP, Ether, srp

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
        self.label = ttk.Label(self.root, text="Active WiFi devices:")
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

    def discover_devices(self):
        if self.scanning:
            live_devices = self.scan_network()

            self.live_devices_data.clear()
            for device_data in live_devices:
                mac_address = device_data[1]
                self.all_devices_data[mac_address] = device_data
                self.live_devices_data.add(mac_address)

            self.update_treeview()

            # Print the number of live devices for debugging purposes
            print(f"Live Devices: {len(self.live_devices_data)}")

            # Schedule the discover_devices method to be called after 1000 milliseconds (1 second)
            self.root.after(1000, self.discover_devices)


    def scan_network(self):
        # Use Scapy to send ARP requests and receive responses
        arp = ARP(pdst="192.168.1.1/24")
        ether = Ether(dst="ff:ff:ff:ff:ff:ff")
        packet = ether/arp

        result = srp(packet, timeout=3, verbose=0)[0]

        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        live_devices = [(res[1].psrc, res[1].hwsrc, "Unknown", current_time) for res in result]

        return live_devices

    def update_treeview(self):
        self.tree.delete(*self.tree.get_children())

        for mac_address in self.live_devices_data:
            device_data = self.all_devices_data.get(mac_address, ("", mac_address, "", ""))
            self.tree.insert("", "end", values=device_data)

    def start_scanning(self):
        self.scanning = True
        self.start_button["state"] = tk.DISABLED
        self.stop_button["state"] = tk.NORMAL

        # Start scanning
        self.discover_devices()

    def stop_scanning(self):
        self.scanning = False
        self.start_button["state"] = tk.NORMAL
        self.stop_button["state"] = tk.DISABLED

    def create_directories(self):
        if not os.path.exists(self.base_directory):
            os.makedirs(self.base_directory)

        if not os.path.exists(self.all_devices_directory):
            os.makedirs(self.all_devices_directory)

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
