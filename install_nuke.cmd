@ECHO off
CHCP 65001 >nul
setlocal ENABLEDELAYEDEXPANSION
REM Idempotent: append nuke.pluginAddPath for this toolkit to %UserProfile%\.nuke\init.py
SET "DIRNAME=%~dp0"
SET "DIRNAME=%DIRNAME:~0,-1%"
SET "DIRNAME=%DIRNAME:\=/%"
SET "TEXT=nuke.pluginAddPath(r'%DIRNAME%')"
SET "FILE=%UserProfile%\.nuke\init.py"

IF NOT EXIST "%UserProfile%\.nuke" (
  MKDIR "%UserProfile%\.nuke"
)

IF NOT EXIST "%FILE%" (
  >"%FILE%" ECHO import nuke
)

FIND /C /I "%TEXT%" "%FILE%" >nul 2>nul
IF %ERRORLEVEL% EQU 0 (
  GOTO Success
)

ECHO.>>"%FILE%"
ECHO %TEXT%>>"%FILE%"

FIND /C /I "%TEXT%" "%FILE%" >nul 2>nul
IF %ERRORLEVEL% EQU 0 (
  GOTO Success
) ELSE (
  GOTO Fail
)

:Success
ECHO ----- current init.py -----
TYPE "%FILE%"
ECHO ---------------------------
ECHO [ark_nuke] install OK - restart Nuke
ECHO.
GOTO :EOF

:Fail
ECHO [ark_nuke] install FAILED - edit "%FILE%" manually
ECHO.
EXIT /B 1