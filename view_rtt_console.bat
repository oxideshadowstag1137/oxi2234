@echo off
echo ========================================
echo   RTT Client - Console Log Viewer
echo ========================================
echo.
echo Starting JLink connection...
echo.

start "JLink RTT Connection" "C:\Program Files (x86)\SEGGER\JLink\JLink.exe" -device STM32F103C8 -if SWD -speed 4000 -AutoConnect 1

timeout /t 2 /nobreak >nul

echo.
echo Starting RTT Client...
echo Press Ctrl+C to stop
echo ========================================
echo.

"C:\Program Files (x86)\SEGGER\JLink\JLinkRTTClient.exe"

pause
