#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flash merged firmware to STM32F103C8 via J-Link
"""

import os
import sys
import subprocess
from pathlib import Path

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def flash_firmware(firmware_path):
    """Flash firmware via J-Link"""
    
    print("\n" + "="*60)
    print("MSU FIRMWARE FLASHER")
    print("="*60)
    
    if not os.path.exists(firmware_path):
        print(f"\n[ERROR] Firmware not found: {firmware_path}")
        return False
    
    print(f"\n[FILE] Firmware: {firmware_path}")
    print(f"   Size: {os.path.getsize(firmware_path)} bytes")
    
    # Create JLink script
    jlink_script = Path(firmware_path).parent / "flash_merged.jlink"
    
    # Escape path for JLink (use quotes for paths with spaces)
    script_content = f"""device STM32F103C8
si SWD
speed 4000
connect
h
loadfile "{firmware_path}" 0x08000000
r
g
exit
"""
    
    print(f"\n[SCRIPT] Creating JLink script...")
    with open(jlink_script, 'w') as f:
        f.write(script_content)
    print(f"   [OK] {jlink_script}")
    
    print(f"\n[FLASH] Flashing firmware via JLink...")
    print(f"   Device: STM32F103C8")
    print(f"   Interface: SWD @ 4MHz")
    print(f"   Address: 0x08000000")
    print()
    
    try:
        # SEGGER JLink path (must be first!)
        jlink_cmd = r"C:\Program Files (x86)\SEGGER\JLink\JLink.exe"
        
        if not os.path.exists(jlink_cmd):
            # Try other paths
            jlink_paths = [
                r"C:\Program Files\SEGGER\JLink\JLink.exe",
                "JLinkExe"
            ]
            jlink_cmd = None
            for cmd in jlink_paths:
                if os.path.exists(cmd):
                    jlink_cmd = cmd
                    break
            
            if not jlink_cmd:
                raise FileNotFoundError("SEGGER JLink not found")
        
        print(f"   Using: {jlink_cmd}")
        
        # Run JLink with script
        result = subprocess.run(
            [jlink_cmd, "-CommanderScript", str(jlink_script)],
            capture_output=False,
            text=True
        )
        
        if result.returncode == 0:
            print("\n" + "="*60)
            print("[SUCCESS] FLASH SUCCESSFUL!")
            print("="*60)
            print("\nExpected LED patterns:")
            print("  [1] 3 fast blinks (200ms) = Bootloader running")
            print("  [2] 2 blinks = Booting to application")
            print("  [3] App LED pattern = Application running!")
            print("\nIf you see slow blink (500ms):")
            print("  -> Application validation failed")
            print("  -> Bootloader in OTA mode")
            print("  -> Check firmware header magic number")
            print()
            return True
        else:
            print("\n[ERROR] Flash failed!")
            return False
            
    except FileNotFoundError:
        print("\n[ERROR] JLink not found!")
        print("   Please install SEGGER J-Link Software:")
        print("   https://www.segger.com/downloads/jlink/")
        return False
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        return False

def main():
    workspace = Path(__file__).parent
    firmware_path = workspace / "merged_firmware.bin"
    
    if not firmware_path.exists():
        print(f"[ERROR] Merged firmware not found: {firmware_path}")
        print(f"   Please run merge_firmware.py first:")
        print(f"   python merge_firmware.py")
        return 1
    
    success = flash_firmware(str(firmware_path))
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
