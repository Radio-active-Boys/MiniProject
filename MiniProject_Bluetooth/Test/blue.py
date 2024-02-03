import os
import asyncio
from bleak import BleakScanner
import keyboard

async def discover_devices():
    while not keyboard.is_pressed('q'):  # Press 'q' to exit the loop
        devices = await BleakScanner.discover()
        devices.sort(key=lambda device: device.rssi, reverse=True)  # Sort devices by RSSI in descending order
        print("Discovered devices:")
        for device in devices:
            print(f"  Device: {device.name}, Address: {device.address}, RSSI: {device.rssi}")
        await asyncio.sleep(1)  # Sleep for 1 second before the next scan


if __name__ == "__main__":
    asyncio.run(discover_devices())
