REM ============================================================
REM  setup_task_scheduler.bat
REM  Run this script ONCE as Administrator to register the
REM  daily 8:00 AM task in Windows Task Scheduler.
REM ============================================================
REM
REM  HOW TO RUN:
REM  1. Right-click this file → "Run as administrator"
REM  2. Done. The task will run every day at 08:00 CET.
REM ============================================================

@echo off

REM -- Adjust this to your actual Python path if needed --
set PYTHON=python

REM -- Full path to the batch runner --
set BAT_SCRIPT=%~dp0run_weather_agent.bat

REM -- Task name (visible in Task Scheduler) --
set TASK_NAME=WeatherAgentGottingen

REM -- Delete old task if it exists (ignore error if not found) --
schtasks /delete /tn "%TASK_NAME%" /f 2>nul

REM -- Create the new scheduled task --
schtasks /create ^
  /tn "%TASK_NAME%" ^
  /tr "\"%BAT_SCRIPT%\"" ^
  /sc daily ^
  /st 08:00 ^
  /ru "%USERNAME%" ^
  /rl HIGHEST ^
  /f

if %ERRORLEVEL% == 0 (
    echo.
    echo [SUCCESS] Task "%TASK_NAME%" created.
    echo It will run every day at 08:00 AM using your Windows account.
    echo.
    echo To verify: open Task Scheduler and look for "%TASK_NAME%"
    echo To test now: schtasks /run /tn "%TASK_NAME%"
) else (
    echo.
    echo [ERROR] Failed to create the task. Make sure you ran this as Administrator.
)

pause
