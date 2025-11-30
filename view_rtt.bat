@echo off
:: ====================================================
:: RTT Viewer for MSU Firmware v1.2
:: Simple & Fast RTT logging
:: ====================================================

set JLINK_PATH=C:\Program Files (x86)\SEGGER\JLink
set DEVICE=STM32F103C8
set SPEED=4000
set INTERFACE=SWD

echo ========================================
echo Starting RTT Viewer for MSU v1.2
echo ========================================
echo Device: %DEVICE%
echo Speed: %SPEED% kHz
echo Interface: %INTERFACE%
echo ========================================
echo.

"%JLINK_PATH%\JLinkRTTViewer.exe" -device %DEVICE% -if %INTERFACE% -speed %SPEED% -rtttelnetport 19021

pause
