# Powershell Script: Stop S24 Ultra Edge Server
# Usage: powershell -ExecutionPolicy Bypass -File .\scripts\stop_s24.ps1

Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "🛑 Stopping S24 Ultra Edge Server (app.py)..." -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan

# Termux 내부 app.py 백그라운드 프로세스 종료
adb shell "pkill -f 'python3.*app.py'"

Start-Sleep -Seconds 1

# 프로세스 확인
$check = adb shell "ps aux | grep 'app.py' | grep -v grep"
if (-not $check) {
    Write-Host "✅ [성공] S24 Ultra 서버 프로세스가 안전하게 종료되었습니다." -ForegroundColor Green
} else {
    Write-Host "⚠️ 경고: 강제 종료 실행 (kill -9)..." -ForegroundColor Yellow
    adb shell "pkill -9 -f 'python3.*app.py'"
    Write-Host "✅ 강제 종료 완료." -ForegroundColor Green
}
