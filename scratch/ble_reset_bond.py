import asyncio
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')

from bleak import BleakScanner, BleakClient

TARGET_NAME = "MOVISION HUD1"
TARGET_ADDR = "14:C1:9F:3A:B2:A2"

async def scan_and_find():
    print(f"[SCAN] {TARGET_NAME} searching... (10sec)")
    devices = await BleakScanner.discover(timeout=10.0)
    found = None
    for d in devices:
        name = d.name or ""
        rssi = d.rssi if hasattr(d, 'rssi') else "?"
        if TARGET_ADDR.lower() in d.address.lower() or "movision" in name.lower():
            print(f"  [FOUND] {name} [{d.address}] RSSI={rssi}")
            found = d
        else:
            print(f"  - {name or '(noname)'} [{d.address}] RSSI={rssi}")
    return found

async def try_connect_with_retry(address: str, max_attempts: int = 3):
    for attempt in range(1, max_attempts + 1):
        timeout = 15 * attempt
        print(f"\n[CONNECT {attempt}/{max_attempts}] {address} (timeout: {timeout}s)")
        try:
            client = BleakClient(address, timeout=float(timeout))
            try:
                await client.connect(dangerous_use_handle_cache=False)
            except TypeError:
                await client.connect()
            if client.is_connected:
                print(f"  [OK] Connected!")
                return client
            else:
                print(f"  [FAIL] is_connected=False")
        except Exception as e:
            print(f"  [ERROR] {type(e).__name__}: {e}")
            if attempt < max_attempts:
                wait_sec = 3 * attempt
                print(f"  Retrying in {wait_sec}s...")
                await asyncio.sleep(wait_sec)
    return None

async def explore_services(client: BleakClient):
    print("\n[SERVICES]")
    try:
        services = client.services
        if not services:
            print("  (no services - possible GATT cache issue)")
            return
        for svc in services:
            print(f"\n  Service: {svc.uuid}")
            print(f"    Desc: {svc.description}")
            for char in svc.characteristics:
                props = ", ".join(char.properties)
                print(f"    Char: {char.uuid}")
                print(f"      Props: {props}")
                if "read" in char.properties:
                    try:
                        val = await client.read_gatt_char(char.uuid)
                        print(f"      Read: {val.hex() if val else '(empty)'}")
                    except Exception as re:
                        print(f"      Read failed: {re}")
    except Exception as e:
        print(f"  [ERROR] Service exploration: {e}")

async def main():
    print("=" * 60)
    print("  MOVISION BLE Connection Diagnostic")
    print("=" * 60)

    device = await scan_and_find()
    if not device:
        print(f"\n[WARN] {TARGET_NAME} not found. Trying direct address...")
        target_addr = TARGET_ADDR
    else:
        target_addr = device.address

    client = await try_connect_with_retry(target_addr, max_attempts=3)

    if client is None:
        print("\n" + "=" * 60)
        print("[FAIL] Connection failed. Try these steps:")
        print("  1. Power cycle HUD (unplug USB, wait 10s)")
        print("  2. Windows: Remove MOVISION from BT devices list")
        print("  3. Disable/Re-enable BT adapter")
        print("  4. NVS bond reset via idf.py monitor")
        print("=" * 60)
        return

    try:
        await explore_services(client)
    finally:
        await client.disconnect()
        print("\n[DONE] Disconnected.")

if __name__ == "__main__":
    asyncio.run(main())
