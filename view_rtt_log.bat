@echo off
echo ========================================
echo   RTT Viewer - MSU Firmware Logging
echo ========================================
echo.
echo Starting JLink RTT Viewer...
echo Device: STM32F103C8
echo Interface: SWD @ 4MHz
echo.

start "" "C:\Program Files (x86)\SEGGER\JLink\JLinkRTTViewer.exe" -device STM32F103C8 -if SWD -speed 4000

echo.
echo RTT Viewer window opened!
echo If it doesn't connect, make sure:
echo   1. J-Link is connected to STM32
echo   2. Firmware is running
echo   3. RTT is initialized in code
echo.
pause
