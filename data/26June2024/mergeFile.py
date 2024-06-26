import json

# Paths to the input JSON files and the output JSON file
file1_path = r'data\26June2024\pie1_data_24_june.json'
file2_path = r'data\26June2024\pie2_data_24_june.json'
output_file_path = r'data\26June2024\merged_file.json'

# Load the data from the first JSON file
with open(file1_path, 'r') as file1:
    data1 = json.load(file1)

# Load the data from the second JSON file
with open(file2_path, 'r') as file2:
    data2 = json.load(file2)

# Create a dictionary to store merged data
merged_data = {}

# Helper function to merge lists
def merge_lists(list1, list2):
    return list(set(list1 + list2))

# Process the first file and store data in the dictionary
for item in data1:
    mac = item['MAC_add']
    if mac not in merged_data:
        merged_data[mac] = {}
    for key, value in item.items():
        if key == 'MAC_add':
            continue
        if key in merged_data[mac]:
            if isinstance(value, list):
                merged_data[mac][key] = merge_lists(merged_data[mac][key], value)
            else:
                merged_data[mac][key] = value  # Handle non-list value collision appropriately if needed
        else:
            merged_data[mac][key] = value

# Process the second file and merge data based on MAC address
for item in data2:
    mac = item['MAC_add']
    if mac not in merged_data:
        merged_data[mac] = {}
    for key, value in item.items():
        if key == 'MAC_add':
            continue
        if key in merged_data[mac]:
            if isinstance(value, list):
                merged_data[mac][key] = merge_lists(merged_data[mac][key], value)
            else:
                merged_data[mac][key] = value  # Handle non-list value collision appropriately if needed
        else:
            merged_data[mac][key] = value

# Convert the merged data dictionary back to a list
final_data = []
for mac, details in merged_data.items():
    merged_item = {'MAC_add': mac}
    merged_item.update(details)
    final_data.append(merged_item)

# Write the merged data to the output JSON file
with open(output_file_path, 'w') as output_file:
    json.dump(final_data, output_file, indent=4)

print(f"Merged JSON file has been created at {output_file_path}")
