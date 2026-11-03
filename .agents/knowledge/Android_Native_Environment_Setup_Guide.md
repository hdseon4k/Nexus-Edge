# Android Native (NDK / C++ / OpenCV) D드라이브 개발 환경 설치 계획서

> **Target Device**: Samsung Galaxy S24 Ultra (Snapdragon 8 Gen 3)  
> **Host OS**: Windows 11 (Host PC)  
> **Install Target**: `D:\Android\`  
> **Document Type**: Setup Guide & Installation Plan  

---

## 1. 개요 및 D 드라이브 표준 디렉터리 구조

C 드라이브 용량 부족을 방지하고 NDK/CMake 빌드 호환성을 확보하기 위해, 경로명에 공백(Space) 및 한글이 없는 순수 영문 디렉터리로 D 드라이브에 통합 구성합니다.

```
D:\Android\
├── Android Studio/                # Android Studio IDE 설치 경로 (Rabbit 1 / 2026.2.1 Stable)
├── Sdk/                           # Android SDK 루트 (Platform, NDK, CMake)
│   ├── ndk/                       # NDK (27.3.13750724 LTS)
│   ├── cmake/                     # CMake (3.31.6)
│   └── platform-tools/            # adb, fastboot 등
├── .gradle/                       # Gradle 빌드 캐시 및 종속성 패키지 (수십 GB)
└── OpenCV-4.14.0-android-sdk/     # OpenCV 4.14.0 C++ Native 라이브러리
    └── sdk/native/jni/            # JNI 헤더 및 arm64-v8a prebuilt libs
```

---

## 2. 다운로드 대상 목록

| 항목 | 구분 | 다운로드 경로 / 비고 |
| :--- | :--- | :--- |
| **Android Studio** | 필수 | [공식 다운로드 페이지](https://developer.android.com/studio) (`Rabbit 1` / `2026.2.1 Stable`) |
| **OpenCV Android SDK 4.14.0** | 필수 | [OpenCV GitHub Releases](https://github.com/opencv/opencv/releases/tag/4.14.0) (`opencv-4.14.0-android-sdk.zip`) |
| **Samsung Android USB Driver** | 필수 | [삼성 개발자 사이트](https://developer.samsung.com/android-usb-driver) (Windows용 통합 드라이버) |

---

## 3. 단계별 설치 및 조치 절차 (User Action Plan)

### Step 1. 사전 디렉터리 생성 및 Windows 환경 변수 설정 (사용자 조치)
C 드라이브에 빌드 캐시가 쌓이는 것을 방지하기 위해 Gradle 캐시 경로를 D 드라이브로 사전 지정합니다.

1. **디렉터리 생성**: `D:\Android` 폴더를 생성합니다.
2. **시스템 환경 변수 등록** (`Win + S` → "시스템 환경 변수 편집" 검색):
   - **사용자 변수** 또는 **시스템 변수**에 신규 추가:
     - 변수 이름: `GRADLE_USER_HOME`
     - 변수 값: `D:\Android\.gradle`
     - 변수 이름: `ANDROID_HOME`
     - 변수 값: `D:\Android\Sdk`
   - **`Path` 시스템 변수 편집**:
     - `D:\Android\Sdk\platform-tools` 추가 (터미널 어디서나 `adb` 실행 가능하도록 설정)

---

### Step 2. Android Studio 설치 (사용자 조치)
1. 다운로드한 `android-studio-*-windows.exe` 실행.
2. **Choose Install Location** 화면에서 설치 경로를 변경:
   - 기본값: `C:\Program Files\Android\Android Studio`
   - **변경값**: `D:\Android\Android Studio`
3. 설치 진행 및 완료.

---

### Step 3. 초기 실행 마법사 & Android SDK 경로 지정 (사용자 조치)
1. Android Studio 첫 실행 시 설정 가져오기(Do not import settings) 선택.
2. **Install Type**: `Custom` 선택.
3. **SDK Components Setup** 창:
   - **Android SDK Location** 경로를 반드시 변경:
     - 기본값: `C:\Users\<User>\AppData\Local\Android\Sdk`
     - **변경값**: `D:\Android\Sdk`
   - `Android SDK Platform`, `Performance (Intel HAXM 또는 AEHD)` 체크 확인 후 다음 진행 및 설치 완료.

---

### Step 4. SDK Platform, NDK & CMake 빌드 도구 설치 (사용자 조치)
1. Android Studio 환영 화면(또는 상단 메뉴)에서:
   - `More Actions` → `SDK Manager` (또는 `Settings` → `Languages & Frameworks` → `Android SDK`) 이동.
2. **`SDK Platforms`** 탭:
   - **`Android 17 (API Level 37.2)`** 체크 (S24 Ultra One UI 9.0 타깃).
3. **`SDK Tools`** 탭:
   - 우측 하단 **`Show Package Details`** 체크박스 활성화.
   - **`Android SDK Build-Tools`** 확장 → **`37.0.0-rc2`** (및 `36.0.0`) 체크.
   - **`NDK (Side by side)`** 확장 → **`27.3.13750724`** 체크 (LTS 안정화 버전, 선택적 `30.0.16248370`).
   - **`CMake`** 확장 → **`3.31.6`** 체크 (C++20 및 OpenCV 4.x 완벽 호환).
4. `Apply` 클릭하여 다운로드 및 설치 (`D:\Android\Sdk`로 자동 저장).

---

### Step 5. OpenCV Android SDK 배치 (사용자 조치)
1. 다운로드한 `opencv-4.14.0-android-sdk.zip`의 압축을 풉니다.
2. 압축 해제된 폴더 이름을 `OpenCV-4.14.0-android-sdk`로 정리하여 다음 경로에 배치합니다:
   - `D:\Android\OpenCV-4.14.0-android-sdk`
3. 정상 배치 확인 경로:
   - `D:\Android\OpenCV-4.14.0-android-sdk\sdk\native\jni\include` (OpenCV C++ 헤더)
   - `D:\Android\OpenCV-4.14.0-android-sdk\sdk\native\libs\arm64-v8a` (S24용 Native 라이브러리)

---

### Step 6. Samsung USB Driver 및 S24 Ultra 연결 설정 (사용자 조치)
1. **드라이버 설치 (기본 C 드라이브 경로 유지 권장)**:
   - `SAMSUNG_USB_Driver_for_Mobile_Phones.exe` 실행하여 설치합니다.
   - **설치 경로**: 기본값인 `C:\Program Files\Samsung\USB Drivers`를 그대로 유지합니다.
   > [!NOTE]
   > **기본 경로 유지 이유**:
   > - 삼성 USB 드라이버는 개발 툴이나 라이브러리가 아니라, Windows OS 커널이 S24를 인식하기 위한 **장치 드라이버(`.sys`, `.inf`)**입니다.
   > - 설치 용량이 **30MB~50MB 내외**로 극히 적으며, 경로를 D 드라이브 등으로 변경할 경우 Windows PnP(Plug & Play) 서비스가 드라이버 참조 경로를 잃어 ADB 연결 시 기기 인식 실패나 불안정이 발생할 수 있습니다.
2. **S24 Ultra 기기 설정**:
   - `설정` → `휴대전화 정보` → `소프트웨어 정보` → **`빌드번호`를 7번 연속 터치**하여 개발자 모드 활성화.
   - `설정` → 맨 아래 `개발자 옵션` 진입.
   - **`USB 디버깅`** 활성화.
3. **PC와 USB 케이블 연결**:
   - 폰 화면에 "USB 디버깅을 허용하시겠습니까?" 팝업 발생 시 **`이 컴퓨터에서 항상 허용`** 체크 후 확인.

---

## 4. 설치 정상 여부 검증 (Verification Checklist)

PowerShell 터미널을 열고 아래 명령어로 정상 구성을 확인합니다.

1. **ADB 기기 인식 확인**:
   ```powershell
   adb devices
   ```
   - 정상 출력 예시: `<기기시리얼번호>    device` (`unauthorized`가 아님을 확인)
   > [!TIP]
   > **`unauthorized` 상태이거나 "USB 디버깅을 허용하시겠습니까?" 팝업이 나타나지 않는 경우**:  
   > S24 Ultra의 `설정` → `보안 및 개인정보 보호` → **`보안 위험 자동 차단`**을 설정(켬) 후 다시 **해제(사용 안 함)**하면 디버깅 허용 팝업이 즉시 나타납니다.

2. **D 드라이브 SDK & NDK 경로 확인**:
   ```powershell
   Test-Path "D:\Android\Sdk\ndk"
   Test-Path "D:\Android\Sdk\cmake"
   Test-Path "D:\Android\OpenCV-4.14.0-android-sdk\sdk\native\jni"
   ```
   - 모두 `True` 반환 시 완료.

---

## 5. 완료 후 다음 단계 (Phase 1 착수)
환경 구축이 완료되면 [[Phase1_Native_App_Execution_Plan]]에 따라 다음 작업을 순차적으로 진행합니다:
1. `D:\CTO\Nexus-Edge\android\` 내 C++20 / CMake 기반 NDK 신규 프로젝트 뼈대 생성.
2. OpenCV 4.14.0 `arm64-v8a` 및 Camera2 Zero-Copy JNI 브리지 코드 작성.

---
## Connections
- **Related Documents**:
  - [[Phase1_Native_App_Execution_Plan]]
  - [[android_native_app_transition_plan]]
  - [[ADR_006_android_native_app_transition]]
  - [[STATUS]]
  - [[README]]

**Tags**: #Knowledge #Phase1 #Android #NDK
