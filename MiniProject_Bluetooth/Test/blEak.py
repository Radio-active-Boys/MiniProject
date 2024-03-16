import asyncio
import bleak
import os

async def run():
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')  # Clear terminal

        devices = await bleak.BleakScanner.discover()
        for device in devices:
            print(f"Device [Name: {device.name}, Address: {device.address}]")

        await asyncio.sleep(5)  # Wait for 5 seconds before the next scan

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
