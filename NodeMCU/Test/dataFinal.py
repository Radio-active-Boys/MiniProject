import serial
import csv
import re
from serial.tools import list_ports

def detect_com_port():
    ports = list_ports.comports()
    for port in ports:
        if 'USB' in port.description:
            return port.device
    return None

def extract_mac_id(data):
    # Extract MAC address from SRC field
    pattern = r'SRC: ([0-9A-Fa-f]{12})'
    match = re.search(pattern, data)
    if match:
        mac = match.group(1)
        # Format MAC address as XX:XX:XX:XX:XX:XX
        formatted_mac = ':'.join([mac[i:i+2] for i in range(0, len(mac), 2)])
        return formatted_mac
    else:
        return None

def main():
    while True:
        # Detect COM port
        com_port = detect_com_port()
        if com_port is None:
            print("COM port not found. Retrying...")
            continue

        try:
            # Open serial connection
            ser = serial.Serial(com_port, baudrate=115200, timeout=1)

            # Open CSV file for writing
            with open('serial_data.csv', 'w', newline='', encoding='utf-8') as csvfile:
                csv_writer = csv.writer(csvfile)
                csv_writer.writerow(['MAC_Address'])  # Write header

                # Read data from serial port and write to CSV
                while True:
                    try:
                        data = ser.readline().decode('utf-8', errors='ignore').strip()  # Read a line from serial
                        mac_id = extract_mac_id(data)
                        if mac_id:
                            csv_writer.writerow([mac_id])  # Write MAC ID to CSV
                            print("MAC ID written to CSV:", mac_id)
                    except KeyboardInterrupt:
                        print("Stopping...")
                        break

            # Close serial connection
            ser.close()
        except serial.SerialException:
            print("Failed to open serial port. Retrying...")
            continue

if __name__ == "__main__":
    main()
