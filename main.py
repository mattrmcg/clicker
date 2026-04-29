import asyncio
import struct
import hashlib
from bleak import BleakScanner

# CONFIGURATION - Must match your Pico!
MY_UUID = "797CDF70-97D8-4E20-8D2F-950850C09480" # Change to yours
SECRET_SALT = "Networks"
COMPANY_ID = 0xFFFF 

def verify_hash(student_id, received_hash):
    combined = str(student_id) + SECRET_SALT
    expected_hash = hashlib.sha256(combined.encode()).digest()[:2]
    return expected_hash == received_hash

async def main():
    print(f"Searching for Pico beacons with UUID: {MY_UUID}...")
    
    # We use a detection callback to process packets in real-time
    def detection_callback(device, advertisement_data):
        if advertisement_data.manufacturer_data:
            print(f"Found: {device.address} | RSSI: {advertisement_data.rssi}")
            print(f"  Data: {advertisement_data.manufacturer_data}")
            
            # Look for your 0xFFFF key specifically
            if 0xFFFF in advertisement_data.manufacturer_data:
                print("  🎯 TARGET PICO DETECTED!")

    async with BleakScanner(detection_callback):
        # Scan indefinitely until you hit Ctrl+C
        while True:
            await asyncio.sleep(1.0)

if __name__ == "__main__":
    asyncio.run(main())