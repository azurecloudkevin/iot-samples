@echo off
setlocal
::echo "%~dp0.env"
call "%~dp0repo" build %*
