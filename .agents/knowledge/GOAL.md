# Nexus-Edge Project Charter

## 1. 프로젝트 목표 (Core Objective)
비전 AI(AprilTag, Visual SLAM, YOLOv11)와 온디바이스 엣지 AI를 결합하여 물류창고 내 재고 및 지게차의 물리적 위치를 실시간 3D 디지털 트윈으로 전환하고, 재고/바코드 인식률 99.9% 달성 및 ERP 시스템과 완벽하게 동기화한다.

## 2. 주요 세부 목표 (Key Pillars)
1. **Precision & Robust Tracking**: AprilTag (36h11) 및 Visual SLAM/VIO 기반 6DoF 절대 좌표 추정 및 바코드 3D 레이캐스팅 좌표화.
2. **Setup C 온디바이스 엣지 AI 상용화**: 지게차 거치형 엣지 노드 연산으로 대규모 무제한 확장성 확보 및 네트워크 트래픽/통신 공사비 0원 실현.
3. **Digital Twin & ERP 연동**: Godot 4.x 기반 실시간 3D 시뮬레이션 및 Odoo External API 데이터 자동화.

## 3. 핵심 마일스톤 (Milestones)
- [x] Phase 1: 멀티카메라 입력 파이프라인 및 캘리브레이션
- [x] Phase 2: AprilTag 기반 로컬라이제이션 및 좌표 변환
- [ ] Phase 3: YOLOv11 + ZBar 바코드 3D 레이캐스팅 디코딩
- [ ] Phase 4: Godot 디지털 트윈 실시간 연동 및 UI 표출

---
## Connections
- **Hub**: [[README]], [[STATUS]]

#Charter #GOAL #Knowledge
