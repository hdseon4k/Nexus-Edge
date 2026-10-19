# Nexus-Edge Knowledge Base Hub & ADR Guidelines

본 지식 저장소는 Nexus-Edge 프로젝트의 기술적 의사결정 기록(ADR), 개발 세션 요약, 핵심 태스크 내역을 보관하는 Obsidian 호환 지식 허브입니다.

## 1. 지식 베이스 표준 규칙
- **위키링크(Wikilinks)**: 문서 연결 시 확장자 없이 `[[파일명]]` 구문 사용.
- **태그 체계**: 문서 하단에 목적별 태그 추가 (`#Knowledge`, `#ADR`, `#Session`, `#Charter`).
- **허브 연결**: 모든 신규 문서는 `[[GOAL]]`, `[[STATUS]]`, `[[README]]` 중 최소 1개 이상 연결.

## 2. ADR (Architecture Decision Record) 템플릿
```markdown
# ADR_[번호]_[제목]

## Context & Problem Statement
- 발생 배경 및 해결하고자 하는 문제

## Considered Options
- 검토된 대안 목록

## Decision Outcome
- 최종 선택된 아키텍처 및 근거

## Pros & Cons
- 장점 및 트레이드오프

---
## Connections
- **Hub**: [[GOAL]], [[README]]

#ADR #Knowledge
```

## 3. 주요 문서 색인 (Index)
- [[GOAL]]: 프로젝트 헌장 및 핵심 목표
- [[ADR_002_inventory_mapping_feasibility]]
- [[ADR_003_phase1_data_collection]]
- [[ADR_004_phase2_live_poc]]
- [[ADR_005_phase2_pick_and_place_logic]]
- [[Task_20260714]]

---
## Connections
- **Hub**: [[GOAL]]

#Knowledge #README
