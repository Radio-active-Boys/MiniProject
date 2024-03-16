import bluetooth
import time

while True:
    nearby_devices = bluetooth.discover_devices( lookup_names=True )
    new = nearby_devices
    
    for addr, name in nearby_devices:
            print(f"Name: {name}, Address: {addr}")
