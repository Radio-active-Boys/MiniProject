import json
import csv
import uuid

json_file_path = r'data\data28Junee\FilterDataBetweenTwoLocation.json' 
csv_file_path = r'data\data28Junee\Data_28June.csv'

with open(json_file_path, 'r') as json_file:
    data = json.load(json_file)

with open(csv_file_path, mode='w', newline='') as csv_file:
    writer = csv.writer(csv_file)

    header = ['_id', 'MAC_add']
  
    keys = {key for item in data for key in item if key not in ['MAC_add']}
    max_lengths = {key: max(len(item[key]) for item in data if key in item) for key in keys}
    print(keys)
    for key in keys:
        header.extend([f'{key}[{i}]' for i in range(max_lengths[key])])
    
    writer.writerow(header)

    # Reverse the order of items here
    for item in  data:
        row = [uuid.uuid4().hex[:24], item['MAC_add']]
        for key in keys:
            values = item.get(key, [])
            row.extend(values + [''] * (max_lengths[key] - len(values)))
        writer.writerow(row)

print(f"CSV file has been created at {csv_file_path}")
