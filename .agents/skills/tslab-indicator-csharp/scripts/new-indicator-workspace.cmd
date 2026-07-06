@echo off
setlocal
set "SCRIPT_DIR=%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%SCRIPT_DIR%new-indicator-workspace.ps1" -Destination "%~1" -Arity "%~2" -ClassName "%~3"
exit /b %ERRORLEVEL%
