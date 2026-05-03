import asyncio
import struct
import hashlib
from bleak import BleakScanner

# CONFIGURATION - Must match your Pico!
SECRET_SALT = "Networks"
COMPANY_ID = 0xFFFF 

attended = set()

def verify_hash(student_id, received_hash):
    combined = str(student_id) + SECRET_SALT
    expected_hash = hashlib.sha256(combined.encode()).digest()[:2]
    return expected_hash == received_hash

def log_student_as_attended(student_id: int):
    attended.add(student_id)
    print(f"Student {student_id} logged as attended.")

async def main():
    print(f"Searching for Pico beacons")
    
    # We use a detection callback to process packets in real-time
    def detection_callback(device, advertisement_data):
        raw_data = advertisement_data.manufacturer_data.get(COMPANY_ID)

        if raw_data:
            try:
                # 2. Unpack the remaining 6 bytes
                # < = Little Endian
                # I = 4-byte unsigned integer (Student ID)
                # 2s = 2-byte bytes object (The Hash)
                student_id, received_hash = struct.unpack("<I2s", raw_data)
                
                # 3. Re-calculate hash for verification
                combined = str(student_id) + SECRET_SALT
                expected_hash = hashlib.sha256(combined.encode()).digest()[:2]
                
                # 4. Verify and Log
                if received_hash == expected_hash:
                    if student_id not in attended:
                        print(f"VERIFIED: Student {student_id} is present. (RSSI: {advertisement_data.rssi})")
                        log_student_as_attended(student_id)
                else:
                    print(f"WARNING: Received ID {student_id} but Hash failed verification!")
                    
            except Exception as e:
                print(f"Error unpacking data: {e}")

    async with BleakScanner(detection_callback):
        # Scan indefinitely until you hit Ctrl+C
        while True:
            await asyncio.sleep(1.0)

if __name__ == "__main__":
    asyncio.run(main())