# Script khởi chạy đồng thời Backend Django và Frontend React
Write-Host "===================================================" -ForegroundColor Cyan
Write-Host "  KHỞI ĐỘNG HỆ THỐNG ĐÁNH GIÁ CHẤT LƯỢNG NƯỚC AI" -ForegroundColor Green
Write-Host "  Backend Django: http://127.0.0.1:8000" -ForegroundColor Yellow
Write-Host "  Frontend React: http://localhost:5173" -ForegroundColor Yellow
Write-Host "===================================================" -ForegroundColor Cyan

$root = $PSScriptRoot

Start-Process cmd.exe -ArgumentList "/k cd /d `"$root\backend`" && `"$root\.venv\Scripts\python.exe`" manage.py runserver 127.0.0.1:8000"
Start-Sleep -Seconds 2
Start-Process cmd.exe -ArgumentList "/k cd /d `"$root\frontend`" && npm run dev"

Write-Host "`nĐã khởi chạy xong cả hai tiến trình trong cửa sổ riêng." -ForegroundColor Green
Write-Host "Mở trình duyệt truy cập: http://localhost:5173" -ForegroundColor Cyan

