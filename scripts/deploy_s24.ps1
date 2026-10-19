# Powershell Deployment Script: Windows 11 PC -> Samsung Galaxy S24 Ultra (Termux)
# Dynamic Device Target Selection (USB Priority + UTF-8 Encoding Enforced)
# Usage: powershell -ExecutionPolicy Bypass -File .\scripts\deploy_s24.ps1

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

Write-Host "=================================================================" -ForegroundColor Cyan
Write-Host "🚀 Nexus-Edge Setup A: S24 Ultra Deployment Script" -ForegroundColor Cyan
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

# 1. 활성 디바이스 타깃 획득 (USB 케이블 직결 우선 탐색)
$rawDevices = & $adbCmd devices
$unauthList = $rawDevices | Select-String "\tunauthorized$"

if ($unauthList) {
    Write-Host "`n⚠️ [승인 대기] 스마트폰 화면에 'USB 디버깅을 허용하시겠습니까?' 팝업이 떠 있습니다!" -ForegroundColor Yellow
    Write-Host "👉 스마트폰 화면을 켜고 '이 컴퓨터에서 항상 허용' 체크 후 [허용]을 눌러주세요." -ForegroundColor Cyan
    Write-Host "   (승인 후 다시 본 스크립트를 실행하시면 배포가 완료됩니다.)`n" -ForegroundColor Gray
    exit 1
}

$deviceList = $rawDevices | Select-String "\tdevice$"

if (-not $deviceList) {
    Write-Host "`n🔌 USB 직결 장치가 없어 무선 ADB 연결을 시도합니다..." -ForegroundColor Yellow
    & $adbCmd connect 192.168.0.64:41997
    Start-Sleep -Seconds 1
    $rawDevices = & $adbCmd devices
    $deviceList = $rawDevices | Select-String "\tdevice$"
}

if (-not $deviceList) {
    Write-Host "❌ 에러: 연결된 디바이스가 없습니다." -ForegroundColor Red
    Write-Host "   - USB 케이블 연결 확인" -ForegroundColor Yellow
    Write-Host "   - 스마트폰 '개발자 옵션' > 'USB 디버깅' ON 확인" -ForegroundColor Yellow
    Write-Host "   - 스마트폰 화면 잠금 해제 확인" -ForegroundColor Yellow
    exit 1
}

$targetDevice = ($deviceList[0].ToString().Split("`t"))[0].Trim()
Write-Host "✅ Target Active Device: $targetDevice" -ForegroundColor Green

# 2. 기존 실행 중인 서버 프로세스 정지 (선택 사항)
Write-Host "`n🔄 기존 서버 프로세스 정지 시도 중..." -ForegroundColor Yellow
try {
    Invoke-WebRequest -Uri "http://192.168.0.64:5000/api/control/stop" -UseBasicParsing -TimeoutSec 1 | Out-Null
    Write-Host "서버에 종료 명령을 전송했습니다. (API Shutdown)" -ForegroundColor Green
    Start-Sleep -Seconds 1
} catch {
    Write-Host "실행 중인 서버가 없거나 원격 응답 대기 건너뜀." -ForegroundColor Gray
}

# 3. S24 Ultra SDCard 디렉터리 생성 및 전송
$sdcardDir = "/sdcard/Nexus-Edge"
Write-Host "`n📁 소스 코드 다이렉트 전송 중 (PC -> $sdcardDir)..." -ForegroundColor Yellow
& $adbCmd -s $targetDevice shell "mkdir -p $sdcardDir"

& $adbCmd -s $targetDevice push ./src "$sdcardDir/"
& $adbCmd -s $targetDevice push ./config "$sdcardDir/"
& $adbCmd -s $targetDevice push ./scripts "$sdcardDir/"

Write-Host "✅ 소스 코드 및 설정 파일 전송 완료!" -ForegroundColor Green

# 4. 완료 안내
Write-Host "`n🎉 [성공] S24 Ultra 배포가 완료되었습니다!" -ForegroundColor Green
Write-Host "-----------------------------------------------------------------" -ForegroundColor Cyan
Write-Host "📌 스마트폰(Termux)에서 다음 명령어로 서버를 실행하세요:" -ForegroundColor Yellow
Write-Host "   cd /sdcard/Nexus-Edge" -ForegroundColor White
Write-Host "   python src/app.py" -ForegroundColor White
Write-Host "-----------------------------------------------------------------" -ForegroundColor Cyan
