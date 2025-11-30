#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MSU Firmware Merge Tool
Merges bootloader and application binaries into a single firmware image

Memory Layout:
  0x08000000-0x08001FFF: Bootloader (8KB)
  0x08002000-0x0800FFFF: Application (56KB)
"""

import os
import sys
import struct
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Constants
BOOTLOADER_START = 0x08000000
BOOTLOADER_SIZE = 8 * 1024  # 8KB allocation
APP_START = 0x08002000
APP_SIZE = 56 * 1024  # 56KB allocation (but actual size much smaller)

# For merged file: only create file big enough for actual content
# This saves space for storage/transmission while JLink can still flash to correct addresses

def read_binary(filepath):
    """Read binary file and return bytes"""
    with open(filepath, 'rb') as f:
        return bytearray(f.read())

def write_binary(filepath, data):
    """Write bytes to binary file"""
    with open(filepath, 'wb') as f:
        f.write(data)

def merge_firmware(bootloader_path, app_path, output_path):
    """
    Merge bootloader and application into single firmware image
    
    Args:
        bootloader_path: Path to bootloader binary (.bin)
        app_path: Path to application binary (.bin)
        output_path: Path to output merged firmware (.bin)
    """
    print("\n" + "="*60)
    print("MSU FIRMWARE MERGE TOOL")
    print("="*60)
    
    # Read bootloader
    print(f"\n[1] Reading bootloader: {bootloader_path}")
    if not os.path.exists(bootloader_path):
        print(f"[ERROR] Bootloader not found: {bootloader_path}")
        return False
    
    bootloader = read_binary(bootloader_path)
    print(f"    [OK] Bootloader size: {len(bootloader)} bytes ({len(bootloader)/1024:.2f} KB)")
    
    if len(bootloader) > BOOTLOADER_SIZE:
        print(f"    [ERROR] Bootloader too large! {len(bootloader)} > {BOOTLOADER_SIZE}")
        return False
    print(f"    [OK] Fits in 8KB allocation ({len(bootloader)*100/BOOTLOADER_SIZE:.1f}% used)")
    
    # Read application
    print(f"\n[2] Reading application: {app_path}")
    if not os.path.exists(app_path):
        print(f"[ERROR] Application not found: {app_path}")
        return False
    
    app = read_binary(app_path)
    print(f"    [OK] Application size: {len(app)} bytes ({len(app)/1024:.2f} KB)")
    
    if len(app) > APP_SIZE:
        print(f"    [ERROR] Application too large! {len(app)} > {APP_SIZE}")
        return False
    print(f"    [OK] Fits in 56KB allocation ({len(app)*100/APP_SIZE:.1f}% used)")
    
    # Check firmware header
    print(f"\n[3] Validating firmware header...")
    if len(app) >= 4:
        magic = struct.unpack('<I', app[0:4])[0]
        print(f"    Magic number: 0x{magic:08X}")
        if magic == 0xDEADBEEF:
            print(f"    [OK] Firmware header valid!")
        else:
            print(f"    [WARN] Firmware header magic mismatch! Expected 0xDEADBEEF")
    
    # Create merged firmware (only as big as needed, not full 64KB)
    print(f"\n[4] Creating merged firmware...")
    
    # Calculate actual size needed: 8KB bootloader section + actual app size
    app_offset = APP_START - BOOTLOADER_START  # 8KB = 0x2000
    merged_size = app_offset + len(app)  # Only size we actually need
    
    merged = bytearray(merged_size)
    
    # Fill with 0xFF (erased flash value)
    for i in range(merged_size):
        merged[i] = 0xFF
    
    # Copy bootloader to start
    merged[0:len(bootloader)] = bootloader
    print(f"    [OK] Copied bootloader @ 0x{BOOTLOADER_START:08X}")
    
    # Copy application at offset 8KB
    merged[app_offset:app_offset+len(app)] = app
    print(f"    [OK] Copied application @ 0x{APP_START:08X}")
    
    # Calculate usage
    total_flash = 64 * 1024  # STM32F103C8 has 64KB flash
    print(f"\n[5] Memory Statistics:")
    print(f"    Bootloader:  {len(bootloader):6} bytes (0x08000000-0x{BOOTLOADER_START+len(bootloader)-1:08X})")
    print(f"    Gap:         {BOOTLOADER_SIZE-len(bootloader):6} bytes (padding)")
    print(f"    Application: {len(app):6} bytes (0x{APP_START:08X}-0x{APP_START+len(app)-1:08X})")
    print(f"    Merged file: {merged_size:6} bytes ({merged_size/1024:.2f} KB)")
    print(f"    Flash used:  {merged_size*100/total_flash:.1f}% ({merged_size}/{total_flash})")
    print(f"    Flash free:  {total_flash-merged_size:6} bytes ({(total_flash-merged_size)/1024:.1f} KB) - Available for EEPROM/config")
    
    # Write output
    print(f"\n[6] Writing merged firmware: {output_path}")
    write_binary(output_path, merged)
    print(f"    [OK] Written {len(merged)} bytes ({len(merged)/1024:.2f} KB)")
    
    print("\n" + "="*60)
    print("[SUCCESS] MERGE COMPLETED SUCCESSFULLY!")
    print("="*60)
    print(f"\nNext steps:")
    print(f"  1. Flash merged firmware:")
    print(f"     JLinkExe -device STM32F103C8 -if SWD -speed 4000 -autoconnect 1")
    print(f"     > loadfile {output_path} 0x08000000")
    print(f"     > r")
    print(f"     > g")
    print(f"\n  2. Observe LED pattern:")
    print(f"     - 3 fast blinks = Bootloader running")
    print(f"     - 2 blinks = Booting to application")
    print(f"     - App LED pattern = SUCCESS!")
    print(f"     - Slow blink = App invalid (OTA mode)")
    print()
    
    return True

def main():
    # Paths
    workspace = Path(__file__).parent
    bootloader_path = workspace / "MSU 1.2 Bootloader Safe" / ".pio" / "build" / "bootloader_safe" / "firmware.bin"
    app_path = workspace / "MSU 1.2" / ".pio" / "build" / "bluepill_f103c8" / "firmware.bin"
    output_path = workspace / "merged_firmware.bin"
    
    # Check if files exist
    if not bootloader_path.exists():
        print(f"❌ Bootloader not found: {bootloader_path}")
        print(f"   Please build bootloader first:")
        print(f'   cd "MSU 1.2 Bootloader Safe"')
        print(f"   pio run")
        return 1
    
    if not app_path.exists():
        print(f"❌ Application not found: {app_path}")
        print(f"   Please build application first:")
        print(f'   cd "MSU 1.2"')
        print(f"   pio run")
        return 1
    
    # Merge firmware
    success = merge_firmware(
        str(bootloader_path),
        str(app_path),
        str(output_path)
    )
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
