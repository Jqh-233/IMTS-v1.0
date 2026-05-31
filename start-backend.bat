@echo off
setlocal
cd /d "%~dp0"
chcp 65001 >nul 2>nul
title IMTS Backend

echo ========================================
echo   IMTS Backend - FastAPI Server
echo ========================================
echo.

:: Check Python
set PYTHON=
for %%e in (python python3 py) do (
    where %%e >nul 2>nul
    if not errorlevel 1 (
        %%e --version >nul 2>nul
        if not errorlevel 1 set PYTHON=%%e
    )
    if defined PYTHON goto :py_ok
)
echo [ERROR] Python not found.
pause
exit /b 1

:py_ok
echo [OK] Python found

:: Setup venv
if not exist ".venv\Scripts\python.exe" (
    echo Creating virtual environment...
    %PYTHON% -m venv .venv
)
echo [OK] Virtual environment ready.

:: Install deps if needed
if not exist ".venv\.deps_installed" (
    echo Installing dependencies (first run)...
    .venv\Scripts\python.exe -m pip install -r backend\requirements.txt -q
    echo installed > ".venv\.deps_installed"
)
echo [OK] Dependencies ready.

echo.
echo Starting on http://localhost:8501
echo Swagger UI: http://localhost:8501/docs
echo.

.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8501 --reload
pause
