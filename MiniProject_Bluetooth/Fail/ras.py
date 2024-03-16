import subprocess
import time

def scan_wifi_networks(output_file, format_type='csv'):
    try:
        # Use 'iwlist' command to scan for available networks
        iwlist_scan = subprocess.check_output(['sudo', 'iwlist', 'wlan0', 'scan'], stderr=subprocess.STDOUT, text=True)
    except subprocess.CalledProcessError as e:
        print(f"Error while scanning WiFi networks: {e.output}")
        return

    # Process the 'iwlist' output to extract network information
    networks = []
    lines = iwlist_scan.split('\n')
    current_network = None

    for line in lines:
        if 'Cell ' in line:
            if current_network:
                networks.append(current_network)
            current_network = {'Cell': line.split(' ')[1]}
        elif 'ESSID:' in line:
            current_network['ESSID'] = line.split(':')[1].strip()
        elif 'Signal level=' in line:
            current_network['Signal Level'] = line.split('=')[1].split(' ')[0]
        elif 'Channel:' in line:
            current_network['Channel'] = line.split(':')[1]
        elif 'Encryption key:' in line:
            current_network['Encryption'] = 'Yes' if line.split(':')[1].strip() == 'on' else 'No'

    if current_network:
        networks.append(current_network)

    # Save the data to the specified output file
    with open(output_file, 'w') as file:
        if format_type == 'csv':
            file.write('Cell,ESSID,Signal Level,Channel,Encryption\n')
            for network in networks:
                file.write(f"{network['Cell']},{network.get('ESSID', '')},{network.get('Signal Level', '')},{network.get('Channel', '')},{network.get('Encryption', '')}\n")
        elif format_type == 'json':
            import json
            json.dump(networks, file, indent=2)
        else:
            print(f"Unsupported format: {format_type}")

# Specify the number of iterations
num_iterations = 5

# Specify the format in which you want to save the data (e.g., 'csv', 'json')
output_format = 'csv'

# Run the scan_wifi_networks function iteratively
for iteration in range(1, num_iterations + 1):
    # Specify the output file name for each iteration
    output_file = f'output_iteration_{iteration}.{output_format}'

    # Run the WiFi scan and save the data
    scan_wifi_networks(output_file, format_type=output_format)

    print(f'Iteration {iteration} completed. Data saved to {output_file}')

    # Introduce a delay between iterations if needed
    time.sleep(5)  # Adjust the delay time as needed