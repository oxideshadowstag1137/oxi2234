#!/usr/bin/env python3
"""
Start J-Link RTT Viewer for MSU Firmware
Allows real-time log viewing without UART
"""

import subprocess
import os
import sys

def start_rtt_viewer():
    """Start J-Link RTT Viewer"""
    
    print("=" * 60)
    print("Starting J-Link RTT Viewer for STM32F103C8")
    print("=" * 60)
    
    # J-Link RTT Viewer command
    # You can use either:
    # 1. JLinkRTTViewer (GUI)
    # 2. JLinkRTTClient (Console)
    # 3. JLinkRTTLogger (Log to file)
    
    try:
        # Option 1: GUI Viewer (Recommended)
        print("\n[Option 1] Starting RTT Viewer (GUI)...")
        print("Command: JLinkRTTViewer -device STM32F103C8 -if SWD -speed 4000")
        print("\nIf JLinkRTTViewer is not found, try:")
        print("- Option 2: JLinkRTTClient (Console)")
        print("- Option 3: JLinkRTTLogger (File logging)")
        
        subprocess.run([
            "JLinkRTTViewer",
            "-device", "STM32F103C8",
            "-if", "SWD",
            "-speed", "4000",
            "-rtttelnetport", "19021"
        ])
        
    except FileNotFoundError:
        print("\n⚠️  JLinkRTTViewer not found in PATH")
        print("\nAlternative methods:")
        print("\n1. Use JLinkRTTClient (Console):")
        print("   JLinkRTTClient")
        print("\n2. Use JLinkExe with RTT:")
        print("   JLinkExe -device STM32F103C8 -if SWD -speed 4000 -autoconnect 1")
        print("   Then start RTT with: connect")
        print("\n3. Manual connection:")
        print("   - Run: JLinkExe -device STM32F103C8 -if SWD -speed 4000")
        print("   - Type: connect")
        print("   - In another terminal: JLinkRTTClient")
        
        return False
    
    return True

if __name__ == "__main__":
    start_rtt_viewer()
