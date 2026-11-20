@ECHO off
CHCP 65001 >nul
setlocal ENABLEDELAYEDEXPANSION
REM Idempotent: remove nuke.pluginAddPath for this toolkit from %UserProfile%\.nuke\init.py
SET "DIRNAME=%~dp0"
SET "DIRNAME=%DIRNAME:~0,-1%"
SET "DIRNAME=%DIRNAME:\=/%"
SET "TEXT=nuke.pluginAddPath(r'%DIRNAME%')"
SET "FILE=%UserProfile%\.nuke\init.py"
SET "TMPFILE=%UserProfile%\.nuke\init.py.ark_nuke_uninstall"

IF NOT EXIST "%FILE%" (
  ECHO [ark_nuke] already uninstalled - init.py not found
  ECHO.
  GOTO :EOF
)

FINDSTR /X /I /C:"%TEXT%" "%FILE%" >nul 2>nul
IF ERRORLEVEL 1 GOTO Already

FINDSTR /X /V /I /C:"%TEXT%" "%FILE%" > "%TMPFILE%"
IF ERRORLEVEL 2 GOTO Fail

MOVE /Y "%TMPFILE%" "%FILE%" >nul
IF ERRORLEVEL 1 GOTO Fail
GOTO Success

:Already
ECHO ----- current init.py -----
TYPE "%FILE%"
ECHO ---------------------------
ECHO [ark_nuke] already uninstalled
ECHO.
GOTO :EOF

:Success
ECHO ----- current init.py -----
TYPE "%FILE%"
ECHO ---------------------------
ECHO [ark_nuke] uninstall OK - restart Nuke
ECHO.
GOTO :EOF

:Fail
IF EXIST "%TMPFILE%" DEL /F /Q "%TMPFILE%"
ECHO [ark_nuke] uninstall FAILED - edit "%FILE%" manually
ECHO.
EXIT /B 1
