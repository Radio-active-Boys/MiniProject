# Bluetooth Device Scanner

🔍 **Bluetooth Device Scanner** is a Python application that scans and monitors Bluetooth devices in real-time. It provides a user-friendly interface to discover nearby Bluetooth devices, export active devices to a CSV file, and maintain a list of unique devices with their discovery time.

## Features

- **Real-time Device Scanning**: 🔄 Continuously scans for nearby Bluetooth devices and displays real-time information.
- **Export to CSV**: 📊 Export a CSV file containing details of currently active devices. The CSV file is named with the timestamp of the export.
- **Unique Devices List**: 📅 Maintain a list of unique devices and their discovery time. Ensures that each device address is unique in the list.
- **On-screen Active Devices**: 📡 Display only the currently active devices on the screen.
- **Time-based Filtering**: ⏱️ Devices are considered active if discovered within a specified time window (e.g., last 10 seconds).

## Getting Started

### Prerequisites

- Python 3.6 or above
- [Bleak](https://pypi.org/project/bleak/) library: `pip install bleak`
- Tkinter library (usually included in Python standard library)

### Installation

1. **Clone the repository**:

   ```bash
   git clone https://github.com/Radio-active-Boys/MiniProject.git
   ```

2. **Install dependencies**:

   ```bash
   cd MiniProject_Bluetooth
   pip install bleak
   ```

### Usage

1. **Run the application**:

   ```bash
   python bluetooth_scanner.py
   ```

2. **Click on "Start Scanning"** to initiate Bluetooth device discovery.
3. **View real-time information** about discovered devices.
4. **Click on "Export to CSV"** to save details of currently active devices. A new CSV file will be created with the export timestamp, and the file will be saved in the List_Active_Devices directory.
5. **Click on "Download List"** to save a list of unique devices and their discovery time. The file will be saved in the List_All_Devices directory.
