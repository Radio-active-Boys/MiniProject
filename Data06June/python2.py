import pandas as pd
import json
import os

# Define file paths
file1_path = 'C:/Users/iitja/Downloads/MiniProject/Data06June/pie1.csv'
file2_path = 'C:/Users/iitja/Downloads/MiniProject/Data06June/pie2.csv'

# Check if files exist
if not os.path.exists(file1_path):
    print(f"File not found: {file1_path}")
    exit(1)

if not os.path.exists(file2_path):
    print(f"File not found: {file2_path}")
    exit(1)

# Load the CSV files
csv1 = pd.read_csv(file1_path)
csv2 = pd.read_csv(file2_path)

# Add a source column to identify the file
csv1['source'] = 'pie1'
csv2['source'] = 'pie2'

# Combine the data
combined_df = pd.concat([csv1, csv2])

# Initialize the result dictionary
result = {}

# Process each row
for _, row in combined_df.iterrows():
    mac = row['MAC_add']
    timestamp = row['Timestamp']
    source = row['source']

    if mac not in result:
        result[mac] = {
            'MAC_add': mac,
            'pie1': [],
            'pie2': []
        }
    
    result[mac][source].append(timestamp)

# Convert the result to a list
result_list = list(result.values())

# Save to JSON file
output_file = 'C:/Users/iitja/Downloads/MiniProject/Data06June/merged_data.json'
with open(output_file, 'w') as f:
    json.dump(result_list, f, indent=4)

print("Data merged and saved to merged_data.json")
