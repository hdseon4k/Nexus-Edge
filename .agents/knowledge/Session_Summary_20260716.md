# Session Summary (2026-07-16)

## 주제: LLM Wiki 및 지식 관리 개념 논의

이번 세션에서는 코드 구현보다는 프로젝트의 지식 관리(Personal Knowledge Management) 및 시스템 작동 원리에 대한 개념적 논의를 진행했습니다.

### 주요 논의 사항
1. **LLM Wiki의 개념:**
   - 마크다운 기반의 로컬 저장소를 활용하여 AI 에이전트(LLM)와 상호작용하는 개인 지식 관리 패턴.
   - 현재 프로젝트의 `.agents/knowledge/` 폴더가 완벽한 LLM Wiki의 역할을 수행 중임을 확인.

2. **RAG (Retrieval-Augmented Generation):**
   - 일반적인 챗봇 형태의 RAG(수동형)와 현재 IDE 에이전트가 사용하는 **'에이전트 기반의 능동형 RAG(Agentic RAG)'**의 차이점 확인.
   - 에이전트가 스스로 파일(ADR 문서 등)을 탐색하고 맥락을 파악하는 원리 이해.

3. **Obsidian (옵시디언) 연동:**
   - 로컬 마크다운 기반의 노트 앱인 옵시디언의 핵심 기능(오프라인, 양방향 링크, 그래프 뷰) 논의.
   - IDE와 옵시디언이 동일한 폴더(`.agents/knowledge`)를 공유(Vault로 지정)함으로써 완벽한 투 트랙(Two-track) 지식 관리 워크플로우를 구축할 수 있음을 확인.

4. **Vault와 Repo의 차이:**
   - **Vault:** 지식의 연결과 탐색(마크다운, 그래프 뷰)에 초점을 맞춘 보관소 개념.
   - **Repo:** 코드의 역사 추적과 협업(Git, 버전 관리)에 초점을 맞춘 저장소 개념.
   - 본 프로젝트는 Git Repo 안에 Obsidian Vault를 품고 있는 이상적인 구조임.

### 향후 방향
- 논의된 아키텍처 결정 사항이나 중요한 구현 로직은 계속해서 `.agents/knowledge/` 내에 ADR 형태로 마크다운 작성 유지.
- 복잡한 문서 간 관계는 옵시디언을 통해 시각화하고, AI 에이전트를 통한 코딩 지원 지속.


## Connections
- **Hub**: [[STATUS]], [[README]]

**Tags**: #Session #Knowledge
