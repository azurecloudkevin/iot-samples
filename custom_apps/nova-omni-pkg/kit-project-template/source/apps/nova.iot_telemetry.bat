@echo off
setlocal
call "%~dp0..\..\kit\kit.exe" "%%~dp0nova.iot_telemetry.kit"  %*
