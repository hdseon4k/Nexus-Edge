# Powershell Deployment Script: Windows 11 PC -> Samsung Galaxy S24 Ultra (Termux)
# Dynamic Device Target Selection
# Usage: powershell -ExecutionPolicy Bypass -File .\scripts\deploy_s24.ps1

Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "🚀 Nexus-Edge Setup A: S24 Ultra Deployment & Execution Script" -ForegroundColor Cyan
Write-Host "=================================================================" -ForegroundColor Cyan

# 0. 최신 Google Official ADB Executable 우선 탐색
$adbCmd = Get-Command adb -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Source
$fallbackPaths = @(
    "d:\GitHub\Nexus-Edge\tools\platform-tools\adb.exe",
    "$PSScriptRoot\..\tools\platform-tools\adb.exe",
    "C:\Program Files\e2eSoft\iVCam\adb\adb.exe"
)

foreach ($path in $fallbackPaths) {
    if (Test-Path $path) {
        $adbCmd = $path
        break
    }
}

if (-not $adbCmd) {
    Write-Host "❌ 에러: 시스템에서 adb.exe 실행 파일을 찾을 수 없습니다." -ForegroundColor Red
    exit 1
}

Write-Host "🔧 ADB Executable: $adbCmd" -ForegroundColor Gray

# 1. 무선 ADB 연결 재연결 시도
Write-Host "`n📡 무선 ADB (192.168.0.64:41997) 연결 확인..." -ForegroundColor Yellow
& $adbCmd connect 192.168.0.64:41997
Start-Sleep -Seconds 1

# 2. 동적 활성 디바이스 타깃 획득
$deviceList = & $adbCmd devices | Select-String "\tdevice$"
if (-not $deviceList) {
    Write-Host "❌ 에러: ADB로 연결된 디바이스가 없습니다. 스마트폰에서 무선 디버깅 ON 상태를 확인하세요." -ForegroundColor Red
    exit 1
}

$targetDevice = ($deviceList[0].ToString().Split("`t"))[0].Trim()
Write-Host "✅ Target Active Device: $targetDevice" -ForegroundColor Green

# 3. 기존 실행 중인 서버 프로세스 정지
Write-Host "`n🔄 기존 서버 프로세스 정지 중..." -ForegroundColor Yellow
try {
    Invoke-WebRequest -Uri "http://192.168.0.64:5000/api/control/stop" -UseBasicParsing -TimeoutSec 2 | Out-Null
    Write-Host "서버에 종료 명령을 전송했습니다. (API Shutdown)" -ForegroundColor Green
    Start-Sleep -Seconds 2
} catch {
    Write-Host "실행 중인 서버가 없거나 응답하지 않습니다." -ForegroundColor Gray
}

# 4. S24 Ultra SDCard 디렉터리 생성 및 전송
$sdcardDir = "/sdcard/Nexus-Edge"
Write-Host "`n📁 소스 코드 무선 전송 중 (SDCard -> $sdcardDir)..." -ForegroundColor Yellow
& $adbCmd -s $targetDevice shell "mkdir -p $sdcardDir"

& $adbCmd -s $targetDevice push ./src "$sdcardDir/"
& $adbCmd -s $targetDevice push ./config "$sdcardDir/"
& $adbCmd -s $targetDevice push ./scripts "$sdcardDir/"

Write-Host "✅ 소스 코드 및 설정 파일 전송 완료!" -ForegroundColor Green

# 5. 완료 안내
Write-Host "`n🎉 [성공] S24 Ultra 무선 배포 완료!" -ForegroundColor Green
Write-Host "-----------------------------------------------------------------" -ForegroundColor Cyan
Write-Host "📌 서버가 꺼져 있습니다. 서버 구동을 위해 다음 단계를 진행하세요!" -ForegroundColor Red
Write-Host "   => 열려있는 SSH 터미널 창에서 다음 명령어를 실행하세요:" -ForegroundColor Yellow
Write-Host "      python src/app.py" -ForegroundColor White
Write-Host "-----------------------------------------------------------------" -ForegroundColor Cyan
