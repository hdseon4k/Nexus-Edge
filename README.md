# 📦 Nexus-Edge
**The Intelligent Bridge between Vision AI and Odoo ERP**

Nexus-Edge는 지능형 물류 시스템의 최전선에서 현장의 물리적 움직임을 디지털 데이터로 전환하는 핵심 엣지 게이트웨이입니다. 액션캠의 고화질 영상을 실시간으로 수집하고, 고성능 PC의 YOLO/OpenCV 연산 결과와 Odoo ERP를 완벽하게 동기화합니다.

### 🚀 Key Objectives
- **Precision:** 비전 기반 인식을 통한 바코드/객체 인식률 99.9% 달성.
- **Integration:** [Odoo External API](https://www.odoo.com)를 통한 실시간 재고 및 공정 데이터 자동화.
- **Agility:** 현장의 액션캠 스트림을 사무실 연산 서버로 전송하는 저지연 파이프라인 구축.

### 🛠 Tech Stack
- **Vision:** [OpenCV](https://opencv.org), [YOLO (Ultralytics)](https://docs.ultralytics.com)
- **Communication:** RTSP Streaming, [XML-RPC / JSON-RPC API](https://www.odoo.com)
- **Environment:** Python 3.x, Linux/Windows Edge Computing

### 📈 Project Status & Transparency
저희는 고객님께 모든 진행 상황을 투명하게 공유합니다.
- **진행 상황 확인:** [GitHub Projects](해당_프로젝트_링크)에서 실시간 칸반 보드 확인 가능
- **테스트 리포트:** `/docs/test-reports` 폴더에서 인식률 검증 결과 상시 공개

## 🛠 시스템 설정 (Configuration)

### 1. 환경 변수 설정
`configs/settings.yaml` 파일에서 Odoo 인스턴스와 카메라 주소를 연결합니다.
- **Odoo URL**: `https://your-odoo-instance.com`
- **Camera Stream**: `rtsp://admin:password@192.168.1.100:554/live`

### 2. 하드웨어 요구사항 (Recommended)
- **Edge Node**: Raspberry Pi 4 (8GB) 또는 동급 IoT Box
- **Inference Server**: NVIDIA RTX 3060 이상 (사무실 고성능 PC)
- **Camera**: 4K 지원 산업용 액션캠 또는 IP 카메라

## 📊 인식률 검증 프로세스 (99.9% Accuracy)
Nexus-Edge는 매일 수집된 데이터 중 인식 실패 사례(0.1%)를 `/docs/test-reports`에 자동 기록합니다.
- **분류**: 조도 저하, 각도 불량, 라벨 훼손 등
- **피드백**: 실패 데이터는 모델 재학습(Retraining)에 즉시 활용되어 인식률을 지속적으로 개선합니다.
