import json
from datetime import datetime, timedelta, timezone

def convert_unix_to_realtime(data):
    ist = timezone(timedelta(hours=5, minutes=30))  # Indian Standard Time (IST)
    for item in data:
        for key in item:
            if isinstance(item[key], list):
                item[key] = [datetime.fromtimestamp(timestamp, ist).strftime('%Y-%m-%d %H:%M:%S') for timestamp in item[key]]
    return data

def main():
    input_file = r'Report\Data6\BetweenTwoLocation.json'
    output_file = r'Report\Data6\ProcessedDataBetweenTwoLocation.json'

    with open(input_file, 'r') as f:
        data = json.load(f)

    converted_data = convert_unix_to_realtime(data)

    with open(output_file, 'w') as f:
        json.dump(converted_data, f, indent=2)

if __name__ == "__main__":
    main()
