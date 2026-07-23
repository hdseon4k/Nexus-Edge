# Powershell Script: Check S24 Ultra Edge Server Status & Logs
# Usage: powershell -ExecutionPolicy Bypass -File .\scripts\status_s24.ps1

Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "🔍 Checking S24 Ultra Edge Server Status & Recent Logs..." -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan

# 프로세스 확인
$process = adb shell "ps aux | grep 'app.py' | grep -v grep"

if ($process) {
    Write-Host "🟢 STATUS: RUNNING (서버가 현재 구동 중입니다)" -ForegroundColor Green
    Write-Host "   Process Info: $process" -ForegroundColor Gray
    
    Write-Host "`n📄 Recent Server Logs (server.log):" -ForegroundColor Yellow
    adb shell "tail -n 15 /data/data/com.termux/files/home/Nexus-Edge/server.log"
} else {
    Write-Host "🔴 STATUS: STOPPED (서버가 켜져있지 않습니다)" -ForegroundColor Red
}
