# Smart Device Scanner 📡🔍

Welcome to the **Smart Device Scanner** project! This Python application is designed to scan and monitor both WiFi and Bluetooth devices, providing a comprehensive solution for network exploration. With an intuitive GUI, real-time scanning, and export options, it's a versatile tool for understanding the devices around you.

## Overview 🚀

The project comprises two scanners:

1. **WiFi Network Scanner** 📡🌐

   - **Real-time Device Scanning**: Continuously scans for connected and available WiFi devices.
   - **Export Options**: Allows exporting scanned data to CSV and JSON files.
   - **User-friendly GUI Interface**: Provides an interactive interface for easy operation.

   For detailed instructions and usage, refer to [WiFi Network Scanner Readme](MiniProject_WiFi/README.md).

2. **Bluetooth Device Scanner** 📡🔵

   - **Real-time Device Scanning**: Continuously scans for nearby Bluetooth devices.
   - **Export to CSV**: Exports details of currently active Bluetooth devices.
   - **Unique Devices List**: Maintains a list of unique devices with their discovery time.
   - **On-screen Active Devices**: Displays only currently active devices.

   For detailed instructions and usage, refer to [Bluetooth Device Scanner Readme](MiniProject_Bluetooth/README.md).

## Prerequisites 🛠️

Ensure you have Python installed on your system.


## Installation 📥

1. **Clone the repository**:

   ```bash
   git clone https://github.com/Radio-active-Boys/MiniProject.git
   ```

2. **Install dependencies**:

   ```bash
   cd MiniProject
   pip install bleak
   pip install wifi
   ```

## Usage 🖥️

1. **Navigate to the respective project directory**:

   - For WiFi Scanner: `cd MiniProject_WiFi`
   - For Bluetooth Scanner: `cd MiniProject_Bluetooth`

2. **Run the application**:

   ```bash
   python wifi_scanner.py  # for WiFi Scanner
   # OR
   python bluetooth_scanner.py  # for Bluetooth Scanner
   ```

3. **Follow the on-screen instructions** for each scanner.

## Happy Scanning! 🌐🔍

Feel the excitement of exploring the devices around you with the Smart Device Scanner. Whether it's WiFi or Bluetooth, this project has got you covered. Happy scanning! 🚀📡🔍


{
  "Unix_TimeStamp": {
    "$elemMatch": {
      "$eq": 1706374815
    }
  }
}


Note: If you want to automate the setup process on multiple Raspberry Pi devices, you can use the provided setup.sh script. Make it executable with the following command:

   ```bash
   chmod +x setup.sh
   ```
