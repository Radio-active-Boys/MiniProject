import serial
import csv
from serial.tools import list_ports

def detect_com_port():
    ports = list_ports.comports()
    for port in ports:
        if 'USB' in port.description:
            return port.device
    return None

def extract_mac_address(data):
    # Find the 'SRC' field in the data
    src_index = data.find('SRC:')
    if src_index != -1:
        # Extract the MAC address substring
        mac_address = data[src_index + len('SRC:'):].split()[0]
        return mac_address
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
                        mac_address = extract_mac_address(data)
                        if mac_address:
                            csv_writer.writerow([mac_address])  # Write MAC address to CSV
                            print("MAC Address written to CSV:", mac_address)
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
