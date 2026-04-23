@echo off
REM ============================================================
REM  run_weather_agent.bat
REM  Run this script to execute the weather agent.
REM  Called automatically by Windows Task Scheduler at 8:00 AM.
REM  Results are saved to weather_log.json.
REM  Open dashboard.html in your browser to view the results.
REM ============================================================

REM -- Set the path to your Python executable --
REM    Use "python" if Python is in your PATH,
REM    or provide the full path, e.g.:
REM    set PYTHON=C:\Users\YourName\AppData\Local\Programs\Python\Python312\python.exe
set PYTHON=C:\Users\mkriegel\AppData\Local\Programs\Python\Python312\python.exe

REM -- Path to the weather agent script --
set SCRIPT_DIR=%~dp0
set SCRIPT=%SCRIPT_DIR%weather_agent.py

REM -- Run the agent --
%PYTHON% "%SCRIPT%"
