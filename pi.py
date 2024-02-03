import asyncio
from bleak import BleakScanner

async def bluetooth_scan():
    devices = await BleakScanner.discover()

    print("Found {} devices.".format(len(devices)))

    for device in devices:
        print("Device Name: {}, Address: {}".format(device.name, device.address))

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(bluetooth_scan())
