# WiFi Network Scanner

This is a simple WiFi network scanner implemented in Python using Tkinter for the GUI. It scans for connected and available devices on the network and provides options to export the data to CSV and JSON files.

## Prerequisites

Make sure you have Python installed on your system.

## Installation

Clone the repository:

```bash
git clone https://github.com/your-username/wifi-network-scanner.git
```
cd wifi-network-scanner
Certainly! Here's a simple README file that you can use. Copy the content below and save it in a file named `README.md` in the same directory as your script.

Install required Python packages:

```bash
pip install wifi
```

## Usage

Run the script:

```bash
python wifi_scanner.py
```

### GUI Interface

- Click the "Start Scanning" button to initiate the device scanning process.
- The scanned devices will be displayed in a Treeview widget.
- Click the "Stop Scanning" button to stop the scanning process.

### Export Options

- "Export All to CSV": Export all scanned devices to a CSV file in the `wifi_scanner_data/all_devices` directory.
- "Export Live to CSV": Export currently connected devices to a CSV file in the `wifi_scanner_data/live_devices` directory.
- "Export to JSON": Export all scanned devices to a JSON file in the `wifi_scanner_data/all_devices` directory.

## Directory Structure

- `wifi_scanner_data/`: Base directory for storing scanned data.
  - `all_devices/`: Directory for storing CSV and JSON files containing all scanned devices.
  - `live_devices/`: Directory for storing CSV files containing currently connected devices.

