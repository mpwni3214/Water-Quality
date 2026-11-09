@echo off
title Water Quality AI - Backend (Django)
echo ===================================================
echo   KHOI DONG BACKEND DJANGO (PORT 8000)
echo ===================================================
cd /d "%~dp0backend"
..\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
pause

