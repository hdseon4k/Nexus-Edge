# S24 Ultra 온디바이스 엣지 AI 전용 앱 전환 개발 계획서
> **Project**: Nexus-Edge (Setup A / Setup C Edge Node)  
> **Document Type**: Architecture & Migration Plan  
> **Target Device**: Samsung Galaxy S24 Ultra (Snapdragon 8 Gen 3 for Galaxy)  

---

## 1. 개요 및 전환 배경 (Executive Summary)

### 1.1 현행(As-Is) Termux 환경의 한계
현재 Nexus-Edge는 S24 Ultra에 **Termux + Python(OpenCV/Flask)** 환경을 구성하여 AprilTag 기반 Visual SLAM 및 텔레메트리 서버를 검증하고 있습니다. 그러나 상용 물류 현장 운영 관점에서 다음과 같은 구조적 한계에 직면해 있습니다:

1. **극심한 CPU 부하 및 발열 스로틀링**:
   - Python 인터프리터 오버헤드와 OpenCV CPU 싱글 스레드 의존으로 AP 코어 온도가 급격히 상승(>48°C), 20~30분 내 CPU Throttling이 걸려 프레임레이트 급락(30fps → 8~12fps).
2. **카메라 파이프라인 버퍼 지연(Zero-copy 불가)**:
   - Camera 스트림을 RTSP 또는 가상 웹캠 파이프라인으로 중계받아 처리하므로 메모리 복사 지연(Frame Buffer Copy Latency 40~60ms) 발생.
3. **OS 백그라운드 관리 취약성 (무인 운영 불가)**:
   - Termux 프로세스는 안드로이드 프레임워크 입장에서 일반 사용자 앱으로 간주되어, Doze 모드(절전) 진입 시 백그라운드 네트워크가 차단되거나 OOM Killer에 의해 상시 강제 종료 위험 존재.
4. **수동 기동 및 유지보수 난이도**:
   - 지게차 전원 인가 시 자동 기동이 불가하며, ADB 명령이나 수동 터미널 명령(`python src/app.py`) 입력 필요.

### 1.2 목표(To-Be) 시스템 정의
- **형태**: 안드로이드 전용 네이티브 데몬 앱 (`NexusEdge-Native`)
- **기술 스택**: Kotlin + C++20 (Android NDK) + OpenCV 4.x C++ Native + NanoHTTPD/Ktor
- **핵심 목표**:
  - Snapdragon 8 Gen 3 하드웨어 가속(Camera2 Zero-copy, Hexagon NPU/Adreno GPU 가속) 적용
  - CPU 점유율 65% 이상 절감 및 발열 스로틀링 원천 차단
  - 지게차 시동(전원 인가) 시 무인 자동 기동 (Boot-Completed Foreground Service)
  - 기존 Godot 4.x / 웹 대시보드와 통신하는 REST API 및 MJPEG 스트림 규격 100% 호환

---

## 2. 목표 시스템 아키텍처 (Target Architecture)

```mermaid
flowchart TB
    subgraph S24_Native_App [Android Native Daemon App (NexusEdge-Native)]
        subgraph Hardware_Access [하드웨어 추상화 계층]
            CAM[Camera2 API / NDK AImageReader]
            NPU[Hexagon NPU / Adreno GPU]
        end
        
        subgraph Native_Core [C++ NDK Native Engine (libnexusedge.so)]
            JNI[JNI Zero-Copy Interface]
            FAST[AprilTag 36h11 C++ Core / Fast Detector]
            PNP[cv::solvePnP 6DoF Pose Solver]
            FILT[EMA / Kalman Smoothing Filter]
            YOLO[QNN / NNAPI YOLOv11 Model Worker]
        end

        subgraph Android_Service [Android OS Service Layer]
            FS[Foreground Service + WakeLock]
            BOOT[Boot-Completed Broadcast Receiver]
            HTTP[Embedded NanoHTTPD / Ktor Server]
        end
    end

    subgraph External_Systems [외부 연동 시스템]
        GODOT[Godot 4.x Digital Twin Engine]
        DASH[Web Dashboard / Survey UI]
    end

    CAM -->|Direct YUV_420_888 Buffer| JNI
    JNI --> FAST & YOLO
    FAST --> PNP --> FILT
    FILT --> HTTP
    YOLO --> HTTP
    FS -.->|Keep Alive & Thermal Monitoring| Native_Core
    BOOT -.->|Auto Start on Power On| FS
    HTTP -->|/api/telemetry (JSON, 30fps)| GODOT
    HTTP -->|/stream.mjpg (640x360)| DASH
```

### 2.1 핵심 구성 모듈
1. **Camera2 & AImageReader Zero-Copy**:
   - Java 힙 메모리를 거치지 않고, NDK 레벨에서 직접 카메라 YUV420 Surface 버퍼 포인터를 취득하여 OpenCV `cv::Mat`으로 즉시 매핑.
2. **C++ Native Vision Pipeline (`libnexusedge.so`)**:
   - `cv::aruco::ArucoDetector` C++ 최적화 및 36h11 패밀리 검출.
   - 2프레임 데시메이션 및 멀티스레딩(OpenMP) 처리.
   - PnP IPPE Square / Iterative 고속 6DoF 자세 추정 및 EMA 자세 보정.
3. **Embedded REST & MJPEG Engine**:
   - 경량 C++ 또는 Kotlin 기반 Embedded HTTP 서버 탑재.
   - 기존 `http://<IP>:5000/api/telemetry`, `http://<IP>:5000/stream.mjpg`, `/api/marker_map` 완전 호환.
4. **산업용 무인 데몬 엔진**:
   - `ForegroundService` + Notification 알림창 유지로 OOM 킬러 대상 제외.
   - `PARTIAL_WAKE_LOCK`을 통해 화면이 꺼진 절전 상태에서도 비전 연산 지속.
   - 전원 공급/부팅 즉시 백그라운드 자동 기동 (`BOOT_COMPLETED`).

---

## 3. 단계별 상세 개발 로드맵 (Phase-by-Phase Roadmap)

### Phase 1: Native 환경 구성 및 Zero-Copy 카메라 파이프라인 (기반 구축)
- [ ] **Android Studio NDK 프로젝트 구성**:
  - Kotlin + C++20 CMake 빌드 환경 (`CMakeLists.txt`) 구성.
  - OpenCV Android NDK SDK 4.10.0 연동 및 ABI(`arm64-v8a`) 최적화 플래그 세팅.
- [ ] **AImageReader 기반 고속 카메라 파이프라인 구현**:
  - Camera2 API를 통해 1080p@60fps 및 서브샘플링(640x360) 해상도 구성.
  - YUV_420_888 평면에서 Y(그레이스케일) 채널을 NDK로 무복사(Zero-copy) 전달하는 JNI 브리지 개발.
- [ ] **기본 스트리밍 검증**:
  - NDK에서 소프트웨어 JPEG 인코딩(TurboJPEG) 후 HTTP MJPEG 스트림 표출 테스트.

### Phase 2: AprilTag SLAM & 6DoF 자세 추정 C++ 포팅 (핵심 비전)
- [ ] **AprilTag 36h11 C++ 검출기 이식**:
  - `src/app.py`에 구현되어 있던 `aruco.DICT_APRILTAG_36h11` 파이프라인을 C++로 완전 포팅.
  - 프레임 데시메이션(Frame skip) 및 바운딩 박스 캐싱 로직 구현.
- [ ] **PnP 포즈 계산 및 EMA 필터 이식**:
  - `marker_map.json` 파싱 모듈 (nlohmann/json C++ 활용).
  - OpenCV `solvePnP` (IPPE Square) 기반 카메라-월드 6DoF ($X, Y, Z, Roll, Pitch, Yaw$) 산출.
  - 각도 불연속 보정(wrap-around)이 포함된 EMA 스무딩 필터 구현.
- [ ] **텔레메트리 REST API 호환**:
  - `/api/telemetry`, `/api/marker_map` 엔드포인트 응답 구현 및 Godot 4.x 연동 확인.

### Phase 3: 무인 자동화 및 산업용 안정성 엔지니어링 (현장 운영)
- [ ] **Foreground Service & WakeLock 구현**:
  - 상시 백그라운드 보장 및 배터리 최적화 예외 처리 (`ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS`).
  - 지게차 시동(충전기 전원 인가) 시 자동 앱 실행 및 부팅 리시버 연동.
- [ ] **온도 기반 동적 연산 제어 (Dynamic Thermal Governor)**:
  - 안드로이드 `ThermalStatusListener` API 연동.
  - 기기 온도가 42°C 초과 시 AprilTag 검출 주기를 2프레임 스킵 → 4프레임 스킵으로 동적 조절하여 스로틀링 다운 방지.
- [ ] **ADB 무인 배포 스크립트 갱신**:
  - Gradle 자동 빌드 및 APK 원격 설치 스크립트 (`deploy_apk.ps1`) 구축.

### Phase 4: NPU 가속화 및 YOLOv11 통합 (지능화 확장)
- [ ] **Qualcomm QNN / ONNX Runtime 연동**:
  - Snapdragon 8 Gen 3 NPU(Hexagon) 전용 QNN 엔진 또는 ONNX Runtime-NNAPI 세팅.
  - YOLOv11n 모델을 INT8 양자화하여 팔레트/바코드 검출 병렬 실행.
- [ ] **24시간 챔버 연속 가동 스트레스 테스트**:
  - 연속 8시간 이상 무중단 포즈 추정 시 메모리 누수, FPS 저하, 과열 여부 검증.

---

## 4. 정량적 기대효과 및 성능 비교

| 평가 항목 | 기존 방식 (Termux + Python) | 전용 네이티브 앱 (Kotlin + NDK C++) | 개선 효과 |
| :--- | :--- | :--- | :--- |
| **평균 CPU 점유율** | 70% ~ 90% (고부하) | **20% ~ 30%** (저부하) | **약 65% 절감** |
| **디바이스 발열** | 45°C ~ 49°C (스로틀링 빈번) | **35°C ~ 38°C** (정상 유지) | **10°C 이상 냉각** |
| **비전 처리 지연(Latency)** | 45ms ~ 65ms | **8ms ~ 15ms** | **4배 반응속도 향상** |
| **운영 안정성** | Doze/OOM에 의해 수시 종료 | **Foreground Service 무중단 24/7** | **무인 운영 가능** |
| **기동 방식** | 터미널 수동 명령 필수 | **전원 인가 시 자동 부팅/실행** | **현장 작업자 개입 제로** |

---

## 5. 결론 및 다음 액션 아이템

전용 앱 전환은 **S24의 하드웨어 잠재력(NPU/Zero-copy)을 100% 인출**하고, B2B 물류 현장에서 필수적인 **발열 해소와 무인 상시 기동성**을 충족하기 위한 필수 단계입니다.

> [!TIP]
> **권장 진행 순서**:
> 1. 기존 Python `app.py`의 핵심 PnP 및 텔레메트리 수식을 C++ 단위 테스트 코드로 검증
> 2. Android Studio 기반 베이스 프로젝트 생성 및 NDK 연동
> 3. 카메라 버퍼 및 AprilTag C++ 파이프라인 우선 구현
