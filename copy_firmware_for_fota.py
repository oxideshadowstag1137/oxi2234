#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copy firmware binary for FOTA distribution
This script copies the application firmware to FOTA_Firmware folder
for CAN-based firmware updates.

Usage:
    python copy_firmware_for_fota.py
"""

import os
import sys
import shutil
import struct
from pathlib import Path
from datetime import datetime

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def analyze_firmware(firmware_path):
    """Analyze firmware binary and extract header info"""
    with open(firmware_path, 'rb') as f:
        data = f.read()
    
    # Check firmware header (first 64 bytes)
    if len(data) < 64:
        return None
    
    magic = struct.unpack('<I', data[0:4])[0]
    version = struct.unpack('<I', data[4:8])[0]
    size = struct.unpack('<I', data[8:12])[0]
    crc32 = struct.unpack('<I', data[12:16])[0]
    flags = struct.unpack('<I', data[16:20])[0]
    
    if magic != 0xDEADBEEF:
        return None
    
    return {
        'magic': magic,
        'version': version,
        'version_str': f"v{(version>>16)&0xFF}.{(version>>8)&0xFF}.{version&0xFF}",
        'size': size,
        'crc32': crc32,
        'flags': flags,
        'actual_size': len(data)
    }

def main():
    print("\n" + "="*60)
    print("MSU FIRMWARE - FOTA PREPARATION")
    print("="*60)
    
    # Paths
    workspace = Path(__file__).parent
    firmware_src = workspace / ".pio" / "build" / "bluepill_f103c8" / "firmware.bin"
    fota_folder = workspace.parent / "FOTA_Firmware"
    
    # Check source firmware
    if not firmware_src.exists():
        print(f"\n❌ Firmware not found: {firmware_src}")
        print(f"   Please build firmware first:")
        print(f"   cd 'MSU 1.2'")
        print(f"   pio run")
        return 1
    
    # Analyze firmware
    print(f"\n[1] Analyzing firmware...")
    info = analyze_firmware(firmware_src)
    
    if not info:
        print(f"   [ERROR] Invalid firmware header!")
        print(f"   Magic number mismatch or file corrupted")
        return 1
    
    print(f"   [OK] Magic:   0x{info['magic']:08X}")
    print(f"   [OK] Version: {info['version_str']} (0x{info['version']:08X})")
    print(f"   [OK] Size:    {info['actual_size']} bytes ({info['actual_size']/1024:.2f} KB)")
    print(f"   [OK] Flags:   0x{info['flags']:08X}")
    
    # Create FOTA folder if not exists
    fota_folder.mkdir(exist_ok=True)
    
    # Generate filename with version and timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"MSU_{info['version_str']}_{timestamp}.bin"
    firmware_dst = fota_folder / filename
    
    # Also create a "latest" copy
    firmware_latest = fota_folder / "MSU_latest.bin"
    
    # Copy firmware
    print(f"\n[2] Copying firmware for FOTA...")
    shutil.copy2(firmware_src, firmware_dst)
    print(f"   [OK] Created: {firmware_dst}")
    
    shutil.copy2(firmware_src, firmware_latest)
    print(f"   [OK] Created: {firmware_latest}")
    
    # Create info file
    info_file = fota_folder / f"MSU_{info['version_str']}_{timestamp}.txt"
    with open(info_file, 'w') as f:
        f.write(f"MSU Firmware Information\n")
        f.write(f"="*60 + "\n\n")
        f.write(f"Version:        {info['version_str']}\n")
        f.write(f"Build Date:     {timestamp[:8]}\n")
        f.write(f"Build Time:     {timestamp[9:].replace('_', ':')}\n")
        f.write(f"File Size:      {info['actual_size']} bytes\n")
        f.write(f"Header Magic:   0x{info['magic']:08X}\n")
        f.write(f"Header Version: 0x{info['version']:08X}\n")
        f.write(f"Header Size:    {info['size']} bytes\n")
        f.write(f"Header Flags:   0x{info['flags']:08X}\n")
        f.write(f"CRC32:          0x{info['crc32']:08X}\n")
        f.write(f"\nMemory Layout:\n")
        f.write(f"  Application: 0x08002000-0x0800FFFF (56KB)\n")
        f.write(f"  This firmware must be flashed to 0x08002000\n")
        f.write(f"\nFOTA Update:\n")
        f.write(f"  Use MSU Production Tool to flash via CAN\n")
        f.write(f"  Or use JLink to flash complete system\n")
    
    print(f"   [OK] Created: {info_file}")
    
    print("\n" + "="*60)
    print("[SUCCESS] FOTA FIRMWARE READY!")
    print("="*60)
    print(f"\nFirmware files:")
    print(f"  [FILE] {filename}")
    print(f"  [FILE] MSU_latest.bin")
    print(f"  📄 {info_file.name}")
    print(f"\nLocation: {fota_folder}")
    print(f"\nYou can now:")
    print(f"  1. Use MSU Production Tool to flash via CAN")
    print(f"  2. Distribute firmware file for field updates")
    print(f"  3. Flash directly to 0x08002000 using JLink")
    print()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
