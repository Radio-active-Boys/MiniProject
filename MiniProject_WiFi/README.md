# WiFi Network Scanner 📡🔍

This is a simple WiFi network scanner implemented in Python using Tkinter for the GUI. It scans for connected and available devices on the network and provides options to export the data to CSV and JSON files.

## Prerequisites 🛠️

Make sure you have Python installed on your system.

## Installation 🚀

Clone the repository:

```bash
git clone https://github.com/Radio-active-Boys/MiniProject.git
```

```bash
cd wifi-network-scanner
pip install wifi
```

## Usage 🖥️

Run the script:

```bash
python wifi_scanner.py
```

### GUI Interface 📱

- Click the "Start Scanning" button to initiate the device scanning process.
- The scanned devices will be displayed in a Treeview widget.
- Click the "Stop Scanning" button to stop the scanning process.

### Export Options 📤

- "Export All to CSV": Export all scanned devices to a CSV file in the `Wifi_Scanner_Data/All_Devices` directory.
- "Export Live to CSV": Export currently connected devices to a CSV file in the `Wifi_Scanner_Data/Live_Devices` directory.
- "Export to JSON": Export all scanned devices to a JSON file in the `Wifi_Scanner_Data/All_Devices` directory.

## Directory Structure 📂

- `Wifi_Scanner_Data/`: Base directory for storing scanned data.
  - `All_Devices/`: Directory for storing CSV and JSON files containing all scanned devices.
  - `Live_Devices/`: Directory for storing CSV files containing currently connected devices.

🚀 Happy Scanning! 📡🔍
