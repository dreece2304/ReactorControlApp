@echo off
:: Disable Windows Auto-Restart for Lab PC
:: Run this script as Administrator

echo ============================================
echo Disabling Windows Auto-Restart Settings
echo ============================================
echo.

:: Check for admin rights
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: Please run this script as Administrator!
    echo Right-click the file and select "Run as administrator"
    pause
    exit /b 1
)

echo [1/5] Disabling auto-restart after updates...
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU" /v NoAutoRebootWithLoggedOnUsers /t REG_DWORD /d 1 /f

echo [2/5] Setting updates to notify only (no auto-install)...
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\WindowsUpdate\AU" /v AUOptions /t REG_DWORD /d 2 /f

echo [3/5] Disabling automatic maintenance restart...
reg add "HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion\Schedule\Maintenance" /v MaintenanceDisabled /t REG_DWORD /d 1 /f

echo [4/5] Disabling sleep and hibernate...
powercfg /change standby-timeout-ac 0
powercfg /change hibernate-timeout-ac 0
powercfg /change standby-timeout-dc 0
powercfg /change hibernate-timeout-dc 0

echo [5/5] Setting high performance power plan...
powercfg /setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c

echo.
echo ============================================
echo Done! Settings applied successfully.
echo ============================================
echo.
echo NOTE: You may need to restart for some
echo       settings to take effect.
echo.
pause
