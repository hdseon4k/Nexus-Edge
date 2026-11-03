# Phase 1: Android Native 프로젝트 구성 및 Zero-Copy 파이프라인 실행 계획서

> **Project**: Nexus-Edge (Setup A / Setup C Edge Node)  
> **Document Type**: Step-by-Step Execution Plan (Phase 1)  
> **Target Device**: Samsung Galaxy S24 Ultra (Snapdragon 8 Gen 3 for Galaxy)  
> **Host Environment**: Windows 11 / `D:\Android\` 툴체인  
> **Target Workspace**: `D:\CTO\Nexus-Edge\android\`  

---

## 1. 개요 및 Phase 1 목표

본 문서는 [[Android_Native_Environment_Setup_Guide]]에 따라 완료된 D드라이브 개발 환경(SDK, NDK 27.3.x, CMake 3.31.6, OpenCV 4.14.0)을 기반으로, [[android_native_app_transition_plan]]의 **Phase 1(Native 환경 구성 및 Zero-Copy 카메라 파이프라인)**을 구체적으로 실행하기 위한 엔지니어링 작업 계획서입니다.

### 1.1 Phase 1 핵심 목표
1. **Android NDK 프로젝트 뼈대 구축**: `D:\CTO\Nexus-Edge\android\`에 Kotlin + C++20 기반 모바일 네이티브 프로젝트 스캐폴딩.
2. **OpenCV 4.14.0 C++ Native 연동**: `arm64-v8a` 아키텍처 타깃으로 `CMakeLists.txt` 및 JNI 브리지 연동.
3. **Camera2 & NDK AImageReader Zero-Copy 파이프라인**: YUV_420_888의 Y(Grayscale) 버퍼 포인터를 Java 힙 복사 없이 C++ `cv::Mat`으로 직결.
4. **임베디드 웹서버(포트 5000) 및 MJPEG 스트리밍**: 640x360 실시간 영상 스트림 송출 및 `/api/telemetry` 기본 응답 호환.
5. **S24 Ultra 실기 배포 검증**: USB 디버깅(ADB)을 통한 APK 설치 및 60fps / 10ms 이하 지연 검증.

---

## 2. 프로젝트 디렉터리 레이아웃 (To-Be)

```
D:\CTO\Nexus-Edge\android\
├── build.gradle.kts                   # 최상위 빌드 스크립트
├── settings.gradle.kts                # 프로젝트/모듈 선언
├── gradle.properties                  # Gradle 데몬 메모리 및 D드라이브 캐시 경로
├── local.properties                   # sdk.dir 및 ndk.dir 명시
├── app/
│   ├── build.gradle.kts               # 앱 모듈 빌드 (NDK, ABI, CMake 설정)
│   ├── CMakeLists.txt                 # C++20 빌드 및 OpenCV 4.14.0 링크 스크립트
│   └── src/
│       └── main/
│           ├── AndroidManifest.xml    # Camera, Service, WakeLock 권한 선언
│           ├── cpp/
│           │   ├── native-lib.cpp     # JNI 엔트리포인트 및 OpenCV 버전/처리 함수
│           │   ├── native_camera.cpp  # AImageReader / Camera2 버퍼 처리
│           │   └── native_camera.h
│           ├── java/com/nexusedge/nativeapp/
│           │   ├── MainActivity.kt    # UI 및 카메라 프리뷰 화면
│           │   ├── camera/
│           │   │   └── Camera2Manager.kt # Camera2 세션 및 AImageReader 바인딩
│           │   ├── server/
│           │   │   └── EdgeHttpServer.kt # 포트 5000 임베디드 웹서버 (NanoHTTPD)
│           │   └── service/
│           │       └── EdgeDaemonService.kt # 무중단 Foreground Service
│           └── res/                   # 레이아웃, 아이콘, 문자열 리소스
```

---

## 3. 단계별 세부 실행 절차 (Step-by-Step Tasks)

### Step 1. Android NDK 프로젝트 뼈대 생성 및 환경 파일 설정
* **작업 내용**:
  - `D:\CTO\Nexus-Edge\android` 디렉터리 생성.
  - `local.properties`에 D드라이브 SDK/NDK 절대 경로 명시:
    ```properties
    sdk.dir=D\:\\Android\\Sdk
    ndk.dir=D\:\\Android\\Sdk\\ndk\\27.3.13750724
    ```
  - `gradle.properties`에 빌드 성능 및 D드라이브 캐시 지정:
    ```properties
    org.gradle.jvmargs=-Xmx4096m -Dfile.encoding=UTF-8
    android.useAndroidX=true
    gradle.user.home=D:/Android/.gradle
    ```
  - `app/src/main/AndroidManifest.xml`에 필수 권한 및 컴포넌트 선언:
    - `android.permission.CAMERA`
    - `android.permission.FOREGROUND_SERVICE`
    - `android.permission.FOREGROUND_SERVICE_CAMERA`
    - `android.permission.WAKE_LOCK`
    - `android.permission.INTERNET`

### Step 2. CMakeLists.txt 구성 및 OpenCV 4.14.0 Native 연동
* **작업 내용**:
  - C++20 표준 활성화 (`set(CMAKE_CXX_STANDARD 20)`).
  - 대상 ABI를 `arm64-v8a`로 고정 (Snapdragon 8 Gen 3 전용 최적화).
  - `D:\Android\OpenCV-4.14.0-android-sdk\sdk\native\jni` 헤더 및 라이브러리 링크:
    ```cmake
    cmake_minimum_required(VERSION 3.22.1)
    project("nexusedge_native")

    set(CMAKE_CXX_STANDARD 20)
    set(OpenCV_DIR "D:/Android/OpenCV-4.14.0-android-sdk/sdk/native/jni")
    find_package(OpenCV REQUIRED)

    add_library(nexusedge SHARED
        native-lib.cpp
        native_camera.cpp
    )

    target_include_directories(nexusedge PRIVATE
        ${OpenCV_INCLUDE_DIRS}
    )

    target_link_libraries(nexusedge
        ${OpenCV_LIBS}
        android
        camera2ndk
        mediandk
        log
    )
    ```
  - JNI 함수 `Java_com_nexusedge_nativeapp_MainActivity_stringFromJNI` 및 `getOpenCVVersion()` 구현으로 연동 검증.

### Step 3. Camera2 & AImageReader Zero-Copy JNI 파이프라인 구현
* **작업 내용**:
  - `Camera2Manager.kt`:
    - S24 Ultra 메인 와이드 카메라(ID: `0` 또는 광각 센서) 선택.
    - 해상도: 1080p (1920x1080) @ 60fps 고정 스트림 요청.
    - `AImageReader` 또는 `ImageReader.newInstance(1920, 1080, ImageFormat.YUV_420_888, 2)` 설정.
  - `native_camera.cpp`:
    - YUV 버퍼 중 Y 평면(포인터 `yBuffer`)을 Java `ByteBuffer`로부터 직접 가져와 `cv::Mat(1080, 1920, CV_8UC1, yPlanePtr)`로 복사 없이 매핑.
    - 연산용 640x360 축소 `cv::resize` (INTER_NEAREST 또는 INTER_LINEAR) 파이프라인 연결.
    - 처리 지연 시간(Timestamp 측정) 로깅.

### Step 4. 임베디드 웹서버 (포트 5000) 및 MJPEG 스트리밍 구성
* **작업 내용**:
  - 경량 HTTP 서버 라이브러리(`org.nanohttpd:nanohttpd:2.3.1`) 의존성 추가.
  - 엔드포인트 구현:
    - `GET /api/telemetry`: JSON 응답 포맷 (기존 `src/app.py` 100% 호환 구조).
      ```json
      {
        "status": "online",
        "fps": 59.8,
        "latency_ms": 7.2,
        "device": "Samsung Galaxy S24 Ultra",
        "battery_temp": 35.2
      }
      ```
    - `GET /stream.mjpg`: NDK에서 인코딩된 640x360 JPEG 프레임을 멀티파트 스트림으로 브로드캐스트.

### Step 5. 빌드 자동화 스크립트 및 S24 Ultra 실기 검증
* **작업 내용**:
  - PowerShell 기반 빌드 & 배포 스크립트 `scripts/deploy_native_apk.ps1` 작성:
    1. Gradle 빌드 (`./gradlew assembleDebug`).
    2. ADB 연결 기기 상태 확인 (`adb devices`).
    3. APK 전송 및 강제 업데이트 설치 (`adb install -r app/build/outputs/apk/debug/app-debug.apk`).
    4. 앱 메인 액티비티 자동 실행 (`adb shell am start -n com.nexusedge.nativeapp/.MainActivity`).
  - S24 Ultra 화면에서 카메라 실시간 뷰 및 FPS/온도 오버레이 확인.
  - PC 브라우저에서 `http://<S24_IP>:5000/stream.mjpg` 스트림 접속 확인.

---

## 4. Phase 1 완료 판정 기준 (Acceptance Criteria)

| 검증 항목 | 목표 기준 | 검증 방법 |
| :--- | :--- | :--- |
| **빌드 & 패키징** | 에러 없이 `app-debug.apk` 빌드 완료 | PowerShell Gradle 빌드 성공 |
| **OpenCV C++ 링크** | OpenCV 4.14.0 라이브러리 함수 정상 호출 | 앱 화면에 OpenCV 4.14.0 버전 문자열 표출 |
| **카메라 파이프라인** | 1080p@60fps 안정 캡처 및 화면 렌더링 | 앱 UI 오버레이에 58~60 FPS 유지 |
| **메모리 복사 지연** | YUV Buffer -> C++ cv::Mat 매핑 8ms 이하 | NDK Logcat 시간 측정 (`__android_log_print`) |
| **웹 스트리밍 호환** | 브라우저/Godot에서 포트 5000 접근 가능 | `http://<S24_IP>:5000/stream.mjpg` 재생 성공 |

---

## 5. 다음 단계 예고 (Phase 2 전환)
Phase 1 검증이 완료되면 즉시 **Phase 2: AprilTag SLAM & 6DoF PnP C++ 포팅**으로 전환하여, 기존 Python `src/app.py`의 핵심 6DoF 자세 추정 알고리즘을 `libnexusedge.so`로 이식합니다.

---

## Connections
- **Related Documents**:
  - [[android_native_app_transition_plan]]
  - [[Android_Native_Environment_Setup_Guide]]
  - [[ADR_006_android_native_app_transition]]
  - [[STATUS]]
  - [[GOAL]]
  - [[README]]

**Tags**: #Phase1 #Android #NDK #ExecutionPlan #Knowledge

