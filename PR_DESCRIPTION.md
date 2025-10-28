# Pull Request: Add A2A Protocol Support for Ticker Score Agent

## 개요

Ticker-Score-Agent를 A2A (Agent-to-Agent) 프로토콜로 래핑하여 다른 에이전트와 통신할 수 있도록 구현했습니다.

## 주요 변경사항

### 1. ADK Agent 래퍼 추가 (app/workflow/a2a_agent.py)
- **calculate_ticker_score**: 기존 LangGraph 워크플로우를 A2A 툴로 래핑
  - Yahoo Finance 데이터, 뉴스, 공시 정보를 분석하여 0-100점 투자 점수 산출
  - 에러 핸들링 및 로깅 포함
- **get_ticker_info**: 에이전트 정보 및 사용 가능한 기능 조회
- LiteLlm(openai/gpt-4o) 모델 사용

### 2. A2A 서버 엔트리포인트 (app/a2a_server.py)
- Google ADK의 `to_a2a()` 유틸리티로 FastAPI 앱 생성
- 포트 8083에서 A2A 프로토콜 서버 실행
- 자동으로 생성되는 엔드포인트:
  - `/.well-known/agent-card.json`: 에이전트 능력 정보
  - `/a2a/execute`: A2A 프로토콜 실행

### 3. Host Agent 예시 (a2a-poc/host/agent_with_ticker.py)
- 기존 agent1, agent2와 함께 ticker_score_agent를 서브 에이전트로 통합
- 멀티 에이전트 오케스트레이션 구현
- 포트폴리오 분석 기능 추가
- 사용 예시:
  - "AAPL 주식을 분석해줘" → ticker_score_agent로 transfer
  - "AAPL, MSFT, NVDA 포트폴리오를 분석해줘" → 각 티커마다 분석 후 종합

### 4. 문서화
- **A2A_SETUP.md**: 상세 설치 및 사용 가이드
  - 실행 방법
  - API 사용 예시
  - A2A 통신 흐름 다이어그램
  - 트러블슈팅
- **test_a2a_setup.py**: 설치 확인 테스트 스크립트
- **README.md**: A2A Protocol Support 섹션 추가

### 5. 의존성 업데이트
- `requirements.txt`에 `google-adk==0.1.0` 추가

## 아키텍처

```
외부 에이전트/Host
    ↓ HTTP POST /.well-known/agent-card.json
    ↓ (에이전트 능력 확인)
    ↓ HTTP POST /a2a/execute
ticker_agent (포트 8083)
    ↓ calculate_ticker_score 호출
    ↓ run_once("AAPL")
LangGraph 워크플로우 실행
    ├─ ingest: 티커 추출
    ├─ yahoo: Yahoo Finance (MCP)
    ├─ dart: 공시 데이터
    ├─ score: LLM 점수 산출
    └─ finalize: 결과 정리
    ↓ JSON 응답 반환
외부 에이전트/Host
```

## 실행 방법

### A2A 서버 실행
```bash
uvicorn app.a2a_server:a2a_app --port 8083 --reload
```

### Agent Card 확인
```bash
curl http://localhost:8083/.well-known/agent-card.json
```

### 기존 REST API와 병렬 운영
```bash
# 터미널 1: REST API
uvicorn app.main:app --port 8080 --reload

# 터미널 2: A2A 서버
uvicorn app.a2a_server:a2a_app --port 8083 --reload
```

### Host Agent로 멀티 에이전트 실행
```bash
# 터미널 1-2: 기존 에이전트
uvicorn a2a-poc.agents.agent1:a2a_app --port 8001
uvicorn a2a-poc.agents.agent2:a2a_app --port 8002

# 터미널 3: Ticker Score Agent
uvicorn app.a2a_server:a2a_app --port 8083 --reload

# 터미널 4: Host Agent
python -m a2a-poc.host.agent_with_ticker
```

## 테스트 계획

- [x] Python 문법 체크 완료
- [x] google-adk 설치 확인
- [x] 모듈 import 테스트
- [ ] A2A 서버 구동 테스트 (환경 설정 후)
- [ ] calculate_ticker_score 툴 실행 테스트
- [ ] Host Agent에서 ticker_agent로 transfer 테스트

## 주요 특징

✅ **기존 코드 재사용**: `run_once()` LangGraph 워크플로우를 그대로 활용
✅ **병렬 운영**: REST API(8080) + A2A 서버(8083) 동시 운영 가능
✅ **표준 프로토콜**: A2A 표준으로 다른 에이전트와 통신
✅ **확장성**: 추가 툴(뉴스 검색, 차트 생성 등)을 쉽게 추가 가능
✅ **에러 핸들링**: try-catch로 안전한 에러 처리
✅ **로깅**: 모든 A2A 호출에 대한 로깅 추가

## 영향 범위

- **기존 기능**: 영향 없음 (REST API는 그대로 유지)
- **새로운 기능**: A2A 프로토콜 지원 추가
- **의존성**: google-adk 추가 (선택적 의존성)

## 변경된 파일

```
A2A_SETUP.md                          (신규 추가) - A2A 설정 가이드
a2a-poc/host/agent_with_ticker.py     (신규 추가) - Host Agent 예시
app/a2a_server.py                     (신규 추가) - A2A 서버
app/workflow/a2a_agent.py             (신규 추가) - ADK Agent 래퍼
requirements.txt                      (수정) - google-adk 추가
test_a2a_setup.py                     (신규 추가) - 테스트 스크립트
README.md                             (수정) - A2A Protocol Support 섹션
```

## 참고 자료

- [Google ADK Documentation](https://github.com/google/adk)
- [A2A Protocol Specification](https://github.com/google/a2a-protocol)
- [A2A_SETUP.md](./A2A_SETUP.md) - 상세 가이드

---

**PR 제목**: `feat: Add A2A Protocol Support for Ticker Score Agent`

**Base 브랜치**: `main`

**Head 브랜치**: `claude/explain-project-structure-011CUaFkTEjTgjXVoatQUmvR`
