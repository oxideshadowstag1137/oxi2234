@echo off
echo ========================================
echo Starting RTT Logger for MSU Firmware
echo ========================================
echo.
echo Step 1: Connecting J-Link...
echo Step 2: Starting RTT output...
echo.
echo Press Ctrl+C to stop
echo ========================================
echo.

"C:\Program Files (x86)\SEGGER\JLink\JLink.exe" -device STM32F103C8 -if SWD -speed 4000 -AutoConnect 1 -RTTTelnetPort 19021

pause
