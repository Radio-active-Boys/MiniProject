import json
import csv
import uuid

# Define paths to input JSON file and output CSV file
json_file_path = r'data\26June2024\ProcessedDataBetweenTwoLocation.json'  # Update with the actual path to your JSON file
csv_file_path = r'data\26June2024\output.csv'

# Load JSON data from the file
with open(json_file_path, 'r') as json_file:
    data = json.load(json_file)

# Create and write to CSV
with open(csv_file_path, mode='w', newline='') as csv_file:
    writer = csv.writer(csv_file)
    
    # Write header
    header = ['_id', 'MAC_add']
    
    # Find all keys and determine the maximum lengths
    keys = {key for item in data for key in item if key not in ['MAC_add']}
    max_lengths = {key: max(len(item[key]) for item in data if key in item) for key in keys}
    
    # Extend header with indices for each key
    for key in keys:
        header.extend([f'{key}[{i}]' for i in range(max_lengths[key])])
    
    writer.writerow(header)
    
    # Write data rows
    for item in data:
        row = [uuid.uuid4().hex[:24], item['MAC_add']]
        for key in keys:
            values = item.get(key, [])
            row.extend(values + [''] * (max_lengths[key] - len(values)))
        writer.writerow(row)

print(f"CSV file has been created at {csv_file_path}")
