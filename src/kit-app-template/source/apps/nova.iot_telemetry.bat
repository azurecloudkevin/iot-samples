@echo off
setlocal
call "%~dp0..\..\kit\kit.exe" "%%~dp0nova.iot_telemetry.kit"  %*
copy "%~dp0.env" "%~dp0custom_apps\kit-app-template\_build\windows-x86_64\release\.env"
