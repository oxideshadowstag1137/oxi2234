#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flash Application to 0x08002000 (8KB offset for bootloader)
This script flashes the MSU 1.2 application firmware to address 0x08002000.
The first 8KB (0x08000000-0x08001FFF) is reserved for the bootloader.
"""

import subprocess
import sys
import os
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def find_jlink():
    """Find JLink executable"""
    # Common installation paths
    paths = [
        r"C:\Program Files\SEGGER\JLink\JLink.exe",
        r"C:\Program Files (x86)\SEGGER\JLink\JLink.exe",
    ]
    
    for path in paths:
        if os.path.exists(path):
            return path
    
    return None

def flash_application():
    """Flash application to 0x08002000"""
    # Find JLink
    jlink_path = find_jlink()
    if not jlink_path:
        print("[ERROR] JLink not found!")
        print("Please install SEGGER J-Link Software from:")
        print("https://www.segger.com/downloads/jlink/")
        return False
    
    print(f"[OK] Found JLink: {jlink_path}")
    
    # Check firmware file
    firmware_path = Path("MSU 1.2/.pio/build/bluepill_f103c8/firmware.bin")
    if not firmware_path.exists():
        print(f"[ERROR] Firmware not found: {firmware_path}")
        print("Please build the project first: pio run")
        return False
    
    # Get file size
    file_size = firmware_path.stat().st_size
    print(f"[OK] Firmware found: {file_size} bytes")
    
    # Check if firmware fits in 56KB
    max_size = 56 * 1024  # 56KB
    if file_size > max_size:
        print(f"[ERROR] Firmware too large! {file_size} bytes > {max_size} bytes")
        print("Application area is only 56KB (bootloader uses 8KB)")
        return False
    
    print(f"[OK] Size check OK: {file_size}/{max_size} bytes ({file_size*100//max_size}%)")
    
    # Flash using JLink script
    script_path = "flash_app_to_0x2000.jlink"
    if not os.path.exists(script_path):
        print(f"[ERROR] JLink script not found: {script_path}")
        return False
    
    print(f"\n[FLASH] Flashing application to 0x08002000...")
    print("=" * 60)
    
    cmd = [
        jlink_path,
        "-device", "STM32F103C8",
        "-if", "SWD",
        "-speed", "4000",
        "-autoconnect", "1",
        "-CommanderScript", script_path
    ]
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=False)
        print("=" * 60)
        print("[SUCCESS] Flash complete!")
        print("\n[WARN] IMPORTANT: This is just the APPLICATION firmware.")
        print("   The bootloader is NOT flashed yet.")
        print("   The device will NOT boot correctly without a bootloader.")
        print("\n[INFO] Next steps:")
        print("   1. Redesign bootloader (8KB) with reset mechanism")
        print("   2. Flash bootloader to 0x08000000")
        print("   3. Test complete system (bootloader + app)")
        return True
    except subprocess.CalledProcessError as e:
        print("=" * 60)
        print(f"[ERROR] Flash failed with error code {e.returncode}")
        return False
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Flash MSU Application to 0x08002000 (Option 2: Safe FOTA)")
    print("=" * 60)
    print("Memory Layout:")
    print("  - Bootloader: 8KB  @ 0x08000000-0x08001FFF")
    print("  - Application: 56KB @ 0x08002000-0x0800FFFF")
    print("=" * 60)
    print()
    
    success = flash_application()
    sys.exit(0 if success else 1)
