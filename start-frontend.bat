@echo off
setlocal
cd /d "%~dp0"
chcp 65001 >nul 2>nul
title IMTS Frontend

echo ========================================
echo   IMTS Frontend - Vite Dev Server
echo ========================================
echo.

:: Check Node.js
where node >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Node.js not found.
    echo Install from https://nodejs.org/
    pause
    exit /b 1
)
echo [OK] Node.js found

:: Setup deps
cd frontend
if not exist "node_modules\.deps_installed" (
    echo Installing dependencies (first run)...
    call npm install
    echo installed > "node_modules\.deps_installed"
)
echo [OK] Dependencies ready.

echo.
echo Starting on http://localhost:5173
echo.

call npm run dev
pause
