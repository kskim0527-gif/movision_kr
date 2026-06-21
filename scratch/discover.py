import asyncio
from bleak import BleakScanner, BleakClient

async def main():
    print("Scanning for MOVISION HUD1...")
    devices = await BleakScanner.discover(timeout=5.0)
    target_addr = None
    for d in devices:
        if d.name and "movision" in d.name.lower():
            print(f"Found target device: {d.name} [{d.address}]")
            target_addr = d.address
            break
    
    if not target_addr:
        print("Device not found. Listing all scanned devices:")
        for d in devices:
            print(f"  {d.name} [{d.address}]")
        return
        
    print(f"Connecting to {target_addr}...")
    async with BleakClient(target_addr, timeout=15.0) as client:
        print("Connected! Discovered Services and Characteristics:")
        for service in client.services:
            print(f"\nService: {service.uuid} ({service.description})")
            for char in service.characteristics:
                print(f"  Characteristic: {char.uuid} - Properties: {char.properties}")

if __name__ == "__main__":
    asyncio.run(main())
