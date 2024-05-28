import json
import datetime
import pytz

# Function to convert UNIX timestamp to Indian Standard Time (IST)
def convert_to_ist(unix_timestamp):
    # Convert UNIX timestamp to datetime object
    utc_time = datetime.datetime.fromtimestamp(unix_timestamp, datetime.timezone.utc)
    # Convert UTC time to Indian Standard Time (IST)
    ist_timezone = pytz.timezone('Asia/Kolkata')
    ist_time = utc_time.astimezone(ist_timezone)
    return ist_time.strftime('%Y-%m-%d %H:%M:%S %Z')

# Read the JSON file
with open(r'C:\Users\iitja\Downloads\MiniProject\Report\MovingCar\devices.json', 'r') as file:
    data = json.load(file)

# Get the MAC address for which you want to find timestamps
mac_address = 'D0:49:7C:4E:F0:A2'

# List to store IST timestamps
ist_timestamps = []

# Iterate over each entry in the data
for entry_list in data:
    for entry in entry_list:
        if entry['MAC_add'] == mac_address:
            # Convert UNIX timestamp to IST
            ist_time = convert_to_ist(entry['Timestamp'])
            ist_timestamps.append(ist_time)

# Store the IST timestamps in a new JSON file
output_data = {
    'MAC': mac_address,
    'IST_timestamps': ist_timestamps
}

with open(r'C:\Users\iitja\Downloads\MiniProject\Report\MovingCar\filterMac.json', 'w') as file:
    json.dump(output_data, file, indent=4)
