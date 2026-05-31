@echo off
cd /d "%~dp0"
chcp 65001 >nul 2>nul

echo.
echo   ========================================
echo     IMTS Launcher
echo   ========================================
echo.

echo [1/5] Checking Python...
set PYTHON=

where python >nul 2>nul
if not errorlevel 1 (
    python --version >nul 2>nul
    if not errorlevel 1 set PYTHON=python
)

if not defined PYTHON (
    where python3 >nul 2>nul
    if not errorlevel 1 (
        python3 --version >nul 2>nul
        if not errorlevel 1 set PYTHON=python3
    )
)

if not defined PYTHON (
    where py >nul 2>nul
    if not errorlevel 1 (
        py -3 --version >nul 2>nul
        if not errorlevel 1 set PYTHON=py -3
    )
)

if defined PYTHON goto :py_found
echo   [ERROR] Python not found.
pause
exit /b 1

:py_found
echo   [OK] Python: %PYTHON%

echo [2/5] Checking Node.js...

where node >nul 2>nul
if errorlevel 1 goto :no_node

node --version >nul 2>nul
if errorlevel 1 goto :no_node

echo   [OK] Node.js found
set NO_FRONTEND=0
goto :step3

:no_node
echo   [WARN] Node.js not found - web UI will be skipped
set NO_FRONTEND=1

:step3
echo [3/5] Setting up Python...

if exist ".venv\Scripts\python.exe" goto :venv_ok
echo   Creating virtual environment...
%PYTHON% -m venv .venv
if errorlevel 1 (
    echo   [ERROR] Failed to create venv
    pause
    exit /b 1
)

:venv_ok
echo   [OK] venv ready

if exist ".venv\.deps_installed" goto :deps_ok
echo   Installing Python dependencies (first run)...
.venv\Scripts\python.exe -m pip install -r backend\requirements.txt -q
if errorlevel 1 (
    echo   [ERROR] pip install failed
    pause
    exit /b 1
)
echo installed > ".venv\.deps_installed"
echo   [OK] Dependencies installed
goto :step4

:deps_ok
echo   [OK] Dependencies ready

:step4
echo [4/5] Setting up frontend...

if "%NO_FRONTEND%"=="1" (
    echo   [SKIP] No Node.js
    goto :step5
)

if exist "frontend\node_modules\.deps_installed" goto :npm_ok
echo   Installing frontend dependencies (first run)...
cd frontend
call npm install --silent
cd ..
if errorlevel 1 (
    echo   [WARN] npm install failed, running backend only
    set NO_FRONTEND=1
    goto :step5
)
echo installed > "frontend\node_modules\.deps_installed"
echo   [OK] Dependencies installed
goto :step5

:npm_ok
echo   [OK] Dependencies ready

:step5
echo [5/5] Starting servers...
echo.

start "IMTS-Backend" cmd /c "cd /d "%~dp0" && title IMTS Backend && .venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8501"
echo   Backend  : http://localhost:8501

if "%NO_FRONTEND%"=="1" goto :wait_health

start "IMTS-Frontend" cmd /c "cd /d "%~dp0frontend" && title IMTS Frontend && npm run dev"
echo   Frontend : http://localhost:5173

:wait_health
echo.
echo   Waiting for backend...
echo   (This may take a few seconds on first run)
echo.

:: Wait up to 30 seconds for backend
set TRIES=0
:loop
timeout /t 2 /nobreak >nul
.venv\Scripts\python.exe -c "import urllib.request; urllib.request.urlopen('http://localhost:8501/health')" >nul 2>nul
if not errorlevel 1 goto :ready
set /a TRIES=%TRIES%+1
if %TRIES% LSS 15 goto :loop

echo   [WARN] Backend did not start within 30 seconds.
echo   Check the Backend window for errors.
pause
exit /b 1

:ready
echo.
echo   ========================================
echo     IMTS is ready!
if "%NO_FRONTEND%"=="0" echo     Frontend : http://localhost:5173
echo     Backend  : http://localhost:8501
echo     API Docs : http://localhost:8501/docs
echo   ========================================
echo.
echo   Close server windows to stop.
echo.

if "%NO_FRONTEND%"=="0" (
    start http://localhost:5173
) else (
    start http://localhost:8501/docs
)

pause
