"""
RTT Viewer Launcher for MSU Firmware
Simple Python script to launch JLinkRTTViewer
"""

import subprocess
import os
import sys

# Configuration
JLINK_PATH = r"C:\Program Files (x86)\SEGGER\JLink"
DEVICE = "STM32F103C8"
SPEED = "4000"
INTERFACE = "SWD"
RTT_TELNET_PORT = "19021"

def main():
    print("=" * 50)
    print("RTT Viewer for MSU Firmware v1.2")
    print("=" * 50)
    print(f"Device: {DEVICE}")
    print(f"Speed: {SPEED} kHz")
    print(f"Interface: {INTERFACE}")
    print(f"RTT Telnet Port: {RTT_TELNET_PORT}")
    print("=" * 50)
    print()
    
    # Check if JLink is installed
    rtt_viewer = os.path.join(JLINK_PATH, "JLinkRTTViewer.exe")
    if not os.path.exists(rtt_viewer):
        print(f"ERROR: JLinkRTTViewer not found at: {rtt_viewer}")
        print("Please install SEGGER J-Link Software")
        input("Press Enter to exit...")
        sys.exit(1)
    
    # Launch RTT Viewer
    try:
        cmd = [
            rtt_viewer,
            "-device", DEVICE,
            "-if", INTERFACE,
            "-speed", SPEED,
            "-rtttelnetport", RTT_TELNET_PORT
        ]
        
        print("Launching RTT Viewer...")
        subprocess.run(cmd)
        
    except Exception as e:
        print(f"ERROR: Failed to launch RTT Viewer: {e}")
        input("Press Enter to exit...")
        sys.exit(1)

if __name__ == "__main__":
    main()
