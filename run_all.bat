@echo off
title Water Quality AI - Launcher
echo ===================================================
echo   KHOI DONG HE THONG DANH GIA CHAT LUONG NUOC
echo   Backend Django: http://127.0.0.1:8000
echo   Frontend React: http://localhost:5173
echo ===================================================

start "Django Backend" cmd /k "run_backend.bat"
timeout /t 2 >nul
start "React Frontend" cmd /k "run_frontend.bat"

echo.
echo Ca hai dich vu da duoc khoi dong trong cac cua so rieng biet.
echo Ban co the mo trinh duyet tai: http://localhost:5173

