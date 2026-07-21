# Session Summary: 하드웨어 세팅 검토 및 B2B 의사결정 보고서 완료 (2026-07-22)

## 📌 주요 수행 작업 및 의사결정 내역

### 1. Accsoon CineView 2 SDI 무선 통신 및 RF 스케일링 검토
- **채널 메커니즘**: 물리적 다이얼 그룹 16개 지원. 2.4GHz + 5GHz 듀얼 밴드 자동 주파수 할당.
- **네트워크 공사 여부**: 1:1 독자 무선 RF망을 형성하므로 창고 내 기업용 Wi-Fi나 LTE망 공사비가 0원임.
- **동일 공간 운용 한계**: 16개 그룹이 존재하나, 2,500평 물류창고/700평 야드 내에서는 주파수(RF) 대역폭 포화 문제로 동일 공간 내 **최대 4세트까지만 운영 가능**함을 확인.

### 2. 하드웨어 스펙 문서 및 B2B 분석서 업데이트
- **`hardware_configurations_list.md` & `hardware_setup_b2b_analysis.md`**:
  - Setup B: 별도 네트워크망 불필요 장점과 최대 4세트 운영 제한 단점 반영.
  - 모니터링: `Lenovo Idea Tab Pro Gen 2 (LTE 라우터 연동 권장)`으로 표기 통일 ('공용' 단어 삭제).
  - 운영 온도 및 요구 네트워크 환경 스펙 명시 (Setup A: 0~35°C, Setup B: -10~40°C, Setup C: -10~40°C 전천후 방진방적방한).
  - 광학 줌/전동 줌 관련 텍스트 전면 제거 (고정 화각/표준 렌즈 기준 단가 및 스펙 정립).

### 3. A5 / NotebookLM 슬라이드 4장 맞춤형 보고서 작성 (`docs/보고용.md`)
- **[Slide 1] Setup A (도보형)**: 1/1.3" 센서, 모바일 AP, 0~35°C, <10대 제한, 평균공급가액(제경비일체) 대당 870만 원.
- **[Slide 2] Setup B (원거리 RF)**: APS-C 적층형 센서, RTX 5090 급 GPU 워크스테이션, -10~40°C, 4대 한계, 평균공급가액(제경비일체) 대당 3,660만 원.
- **[Slide 3] Setup C (온디바이스 엣지 AI)**: M4/3 듀얼 ISO 센서, `Nexus Edge (저전력 NPU 포함)` + 10.9" 태블릿, -10~40°C (영하 10도 냉동창고 & 혹서기 야드 대응), 무제한 확장, 평균공급가액(제경비일체) 대당 1,845만 원.
- **[Slide 4] 인프라 TCO 비교표 & 최종 제안**: 3,200평 인프라 비교표 (Wi-Fi 6/7 1,400만~2,200만 원 vs Setup C LTE 라우터 공사비 0원) 및 PoC(Setup B) -> 본사업 최종 운영 체계(Setup C) 확정 제안.

---

## 🔗 관련 문서 및 Wiki-Links
- [[STATUS]]
- [[README]]
- [hardware_configurations_list](file:///d:/GitHub/Nexus-Edge/docs/hardware_configurations_list.md)
- [hardware_setup_b2b_analysis](file:///d:/GitHub/Nexus-Edge/docs/hardware_setup_b2b_analysis.md)
- [보고용](file:///d:/GitHub/Nexus-Edge/docs/보고용.md)

#Session #Knowledge #Hardware #B2B #NexusEdge #TCO
