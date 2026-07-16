# Real-time Warehouse Inventory Mapping System (Feasibility Study)

이 문서는 보유하신 고성능 하드웨어 장비들을 활용하여 이동 중 물류창고 내 박스의 바코드를 인식하고, 해당 위치를 2D 맵에 실시간으로 매핑하는 "재고 조사 시스템"의 타당성 검토 및 하드웨어 배치 계획입니다.

## 🎯 최종 달성 목표 (Core Objective)

이번 타당성 검토(Feasibility Study)의 궁극적인 목표는 **"이동하는 카메라 한 대만으로 창고 내 재고의 절대 위치 지도를 실시간으로 자동 구축할 수 있는가?"**를 실증하는 것입니다. 이를 위해 다음 3단계 기술의 유기적인 결합을 검증합니다.

1. **카메라 포즈 추정 (SLAM)**: SLAM 알고리즘을 통해 카메라가 창고 내 어디에 위치해 있고 어느 곳을 바라보고 있는지(X, Y, Z 및 Roll, Pitch, Yaw 방향)를 실시간으로 파악합니다.
2. **바코드 탐지 및 해독 (Vision AI)**: YOLOv11과 ZBar 앙상블을 통해 2D 영상(픽셀) 화면 상에서 바코드를 찾아내고 해당 제품의 데이터를 해독합니다.
3. **3D 공간 매핑 (Ray Casting & 융합)**: 1단계(카메라 절대 위치/방향)와 2단계(픽셀 정보) 데이터를 융합합니다. 렌즈에서 바코드 픽셀을 향해 가상의 빛(Ray)을 쏘아 거리를 계산함으로써, 최종적으로 **"특정 바코드가 창고의 어느 3D 좌표에 위치해 있는지"**를 산출하고 이를 실시간 지도 위에 기록합니다.

---

## User Review Required

> [!IMPORTANT]
> **Data Collection Phase (파인튜닝 데이터 수집 규격)** 
> 본격적인 테스트 전에 물류창고 현장에서 박스 바코드 영상을 수집하여 통합 YOLOv11 모델을 파인튜닝해야 합니다. AI 모델이 실제 추론 환경(Domain)과 동일한 조건에서 학습할 수 있도록, 셋업별로 다음의 해상도 및 프레임 규격으로 영상을 수집하는 것을 권장합니다.
> *   **Setup A (Insta360)**: `4K (3840x2160) @ 60fps` 
>     - 광각 환경에서 바코드 픽셀이 뭉개지지 않도록 고해상도 필요. 이동 시 모션 블러 방지를 위해 60fps 권장.
> *   **Setup B (Fujifilm X-H2s)**: `FHD (1920x1080) @ 60fps`
>     - 무선 SDI 송수신기(Accsoon)의 최대 전송 대역폭(1080p60)에 맞추어, 서버가 실제로 받게 될 추론 환경과 동일하게 촬영.
> *   **Setup C (M90q + Hailo)**: `FHD (1920x1080) @ 30fps`
>     - 엣지 미니 PC의 영상 디코딩 병목을 방지하고 NPU로 초고속 인퍼런스를 넘기기 위한 최적의 스윗스팟.

---

## 🏗️ SLAM 맵핑 사전 준비사항 (Environmental Pre-requisites)

> [!WARNING]
> 물류창고는 반복되는 패턴(비슷한 모양의 박스와 랙)이 끝없이 이어져 있어, 카메라가 위치를 잃기 쉬운 매우 가혹한 환경입니다. 안정적인 실시간 맵핑을 위해 다음의 현장 사전 작업이 필수적입니다.

### 1. 하이브리드 포지셔닝 준비 (ArUco + VIO)
*   **ArUco 마커 부착 (절대 좌표 교정용)**
    *   창고 내 주요 기둥, 랙의 교차로 모서리 등 지게차나 화물에 가려지지 않는 높은 곳에 A4 크기 이상의 ArUco 마커를 인쇄해 부착합니다.
    *   부착된 각 마커의 실제 절대 위치(X, Y, Z 좌표)를 측정하여 `marker_map.json` 설정 파일로 사전에 구성합니다.
*   **VIO (Visual-Inertial Odometry) 융합 적용**
    *   단순 카메라 영상(Visual)에만 의존하지 않고, Insta360 및 스마트폰에 내장된 **IMU(관성 센서)** 데이터를 결합합니다. 바코드 박스만 화면에 가득 차 특징점이 소실되는 순간에도 센서의 관성으로 위치를 계산해 궤적이 튀는 것을 막습니다.

### 2. 인위적 특징점(Feature Points) 생성
*   **고대비 텍스처(안전 테이프) 추가**: 밋밋한 회색 기둥이나 랙의 프레임 등에 **노란색/검은색 사선 패턴의 안전 테이프**를 부착하여, SLAM 알고리즘이 강한 대비를 통해 코너(Corner) 특징점을 쉽게 잡을 수 있도록 유도합니다.
*   **구역 식별 표지판**: 동일한 모양의 박스가 늘어선 곳곳에 구역을 알리는 고유 색상 및 알파벳 팻말을 달아, 카메라가 랜드마크로 인식할 수 있게 돕습니다.

---

## Hardware Allocation Strategy (하드웨어 테스트 배치 방안)

보유하신 장비의 특성을 극대화하기 위해 목적이 다른 **세 가지 하드웨어 세팅(A, B, C)**을 구성하여 현장 테스트를 진행할 것을 제안합니다.

### Setup A: 작업자 착용형 모바일 허브 세팅 (High-Mobility Wearable)
**목적:** 작업자가 도보로 이동하며 좁은 통로나 하단 선반의 바코드를 스캔하고 실시간 위치(Visual SLAM)를 파악하는 기동성 위주 테스트.
*   **영상 취득:** **Insta360 ace pro 2** 
*   **마운트:** **STUNTMAN 360** 
*   **통합 제어 허브:** **8-port USB-C hub (2.5Gb Ethernet)** (스마트폰과 액션캠 유선 연결 및 보조배터리 전원 공급)
*   **엣지 프로세싱 및 송출:** **갤럭시 S24 Ultra** (자체 1차 연산 및 5G/Wi-Fi 영상 송출)
*   **실시간 모니터링 UI:** **lenovo Idea Tab Pro Gen 2**

### Setup B: 카트/지게차 장착형 원거리 셋업 (Base Station Heavy AI)
**목적:** 중앙 서버(ThinkPad)의 압도적인 연산력을 활용해 무거운 앙상블 디코딩과 원거리 초고화질 탐지를 수행하는 정밀도 테스트.
*   **영상 취득:** **후지필름 X-H2s + 18-120mm 렌즈** 
*   **무선 송수신:** **Accsoon CineView 2 SDI** -> **블랙매직디자인 HDR 12GSDI** 캡처
*   **메인 처리(Base Station):** **ThinkPad T16g Gen 3 (RTX 5090)** 

### Setup C: 카트 장착형 온디바이스 엣지 AI 셋업 (On-Device Edge AI) 
**목적:** 미니 PC와 AI 가속기를 카트/지게차에 직접 탑재하여, 대용량 영상 스트리밍 없이 엣지(현장)에서 실시간 추론을 끝내는 완벽한 Edge AI 아키텍처 테스트.
*   **엣지 컴퓨팅 노드:** **ThinkCentre M90q gen 6 (Tiny PC)**
*   **AI 추론 가속:** **Hailo 10H** (M.2 NPU 가속기)
*   **초경량 네트워크 전송:** M90q 노드에서 영상을 자체 처리하고, **"바코드 데이터 텍스트 + 현재 위치 좌표(x,y,z)"**라는 수 KB 수준의 메타데이터만 사내 Wi-Fi를 통해 중앙 서버로 전송합니다.

---

## 💡 네트워크 인프라 도입 비용 최적화 검증 (Business Value)

> [!TIP]
> **고가의 Wi-Fi 6/7 인프라 구축 비용 절감 증명**
> 이 테스트 계획의 핵심 목적 중 하나는 **네트워크 대역폭 요구사항의 획기적 감소**를 증명하는 것입니다.
> 
> *   **Setup B (중앙 집중형 AI)**의 경우 고화질 영상을 실시간으로 무선 전송해야 하므로, 실제 현장에 도입 시 대규모 창고 전체에 고비용의 Wi-Fi 6/7 또는 전용 5G 특화망 인프라가 강제될 수 있습니다.
> *   **Setup C (On-Device 엣지 AI)**를 채택할 경우 무거운 영상 처리가 현장(Hailo NPU)에서 끝나고 단 몇 바이트(Bytes)의 텍스트 좌표/데이터만 전송됩니다. 
> *   **결과적으로 Setup C를 실증함으로써, 기존 물류창고에 설치된 저렴한 표준 Wi-Fi 4/5 (2.4GHz) 공유기나 LTE 라우터만으로도 끊김 없는 실시간 재고 파악 시스템을 완벽히 구축할 수 있음을 입증하게 됩니다.**

---

## Proposed Software Changes

### 1. 영상 캡처 모듈 (Camera Input Framework)
- `src/camera/stream_manager.py` [NEW]
  - `MobileHubMode`, `SDICaptureMode`, `LocalEdgeMode` 지원.

### 2. 위치 추적 모듈 (Localization Module)
- `src/localization/aruco_slam.py` [NEW] / `src/localization/visual_slam.py` [NEW]

### 3. 디코딩 파이프라인 (Detection & Decoding)
- `src/inference/detector.py` [MODIFY]
  - **Hailo SDK (HailoRT) 연동 로직 추가:** Setup C 환경을 위해 YOLO 모델을 Hailo `.hef` 형식으로 컴파일하고 NPU 위에서 구동하도록 파이프라인 분기 처리.

### 4. 2D 맵 기반 테스트 UI (Visualization)
- `src/app.py` [MODIFY] & `src/static/map_ui.html` [NEW]

## Verification Plan
1. **Hailo 컴파일 테스트**: 기존 YOLOv11 모델을 Hailo Dataflow Compiler를 통해 양자화 및 `.hef`로 변환하고 구동되는지 사전 검증.
2. **네트워크 병목 비교 (Setup B vs C)**: 무압축 무선 영상 전송(Setup B)과 메타데이터 전송(Setup C) 간의 네트워크 트래픽 및 중앙 서버/공유기 부하 차이를 비교 측정.


## Connections
- **Related ADRs**:
  - [[ADR_003_phase1_data_collection]]
  - [[ADR_004_phase2_live_poc]]
  - [[ADR_005_phase2_pick_and_place_logic]]
- **Hub**: [[STATUS]], [[README]]

**Tags**: #ADR #Knowledge
