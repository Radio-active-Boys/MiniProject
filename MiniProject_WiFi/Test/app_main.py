import os
import asyncio
import csv
import tkinter as tk
from tkinter import ttk

class WiFiScannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("WiFi Network Scanner")

        self.networks_data = []
        self.scanning = False

        self.create_widgets()

    def create_widgets(self):
        self.label = ttk.Label(self.root, text="Discovered WiFi networks:")
        self.label.pack(pady=10)

        self.tree = ttk.Treeview(self.root, columns=("SSID", "BSSID", "Signal Strength", "Details"), show="headings")

        self.tree.heading("SSID", text="SSID")
        self.tree.heading("BSSID", text="BSSID")
        self.tree.heading("Signal Strength", text="Signal Strength")
        self.tree.heading("Details", text="Details")

        self.tree.pack(expand=True, fill="both")

        self.start_button = ttk.Button(self.root, text="Start Scanning", command=self.start_scanning)
        self.start_button.pack(pady=10)

        self.stop_button = ttk.Button(self.root, text="Stop Scanning", command=self.stop_scanning, state=tk.DISABLED)
        self.stop_button.pack(pady=10)

        self.export_button = ttk.Button(self.root, text="Export to CSV", command=self.export_to_csv)
        self.export_button.pack(pady=10)

    async def discover_networks(self):
        while self.scanning:
            # Run the command to list available WiFi networks
            result = os.popen("netsh wlan show networks mode=Bssid").read()
            networks = [line.strip() for line in result.split('\n') if line.strip()]

            # Parse the network information
            self.networks_data = [tuple(network.split(': ')[1:]) for network in networks if ':' in network]

            self.update_treeview()
            await asyncio.sleep(1)

    def update_treeview(self):
        self.tree.delete(*self.tree.get_children())

        for network_data in self.networks_data:
            self.tree.insert("", "end", values=network_data)

    def start_scanning(self):
        self.scanning = True
        self.start_button["state"] = tk.DISABLED
        self.stop_button["state"] = tk.NORMAL

        # Run the discover_networks coroutine in the asyncio event loop
        loop = asyncio.get_event_loop()
        loop.create_task(self.discover_networks())

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
        with open('discovered_networks.csv', 'w', newline='') as csvfile:
            fieldnames = ['SSID', 'BSSID', 'Signal Strength', 'Details']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for network_data in self.networks_data:
                writer.writerow({'SSID': network_data[0], 'BSSID': network_data[1], 'Signal Strength': network_data[2], 'Details': network_data[4]})
                
if __name__ == "__main__":
    root = tk.Tk()
    app = WiFiScannerApp(root)
    root.mainloop()
