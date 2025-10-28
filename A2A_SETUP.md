# A2A (Agent-to-Agent) 설정 가이드

## 개요

Ticker-Score-Agent를 A2A 프로토콜로 다른 에이전트와 통신할 수 있도록 설정하는 방법입니다.

## 구조

```
app/
├── main.py              # 기존 REST API (포트 8080)
├── a2a_server.py        # 🆕 A2A 서버 (포트 8083)
└── workflow/
    ├── graph.py         # LangGraph 워크플로우
    └── a2a_agent.py     # 🆕 ADK Agent 래퍼
```

## 설치

```bash
# 의존성 설치
pip install -r requirements.txt

# google-adk가 포함되어 있습니다
```

## 실행 방법

### 1. Ticker Score Agent (A2A 서버)

```bash
# 터미널 1: A2A 서버 실행
uvicorn app.a2a_server:a2a_app --port 8083 --reload
```

실행 후 확인:
- Agent Card: http://localhost:8083/.well-known/agent-card.json
- Execute Endpoint: http://localhost:8083/a2a/execute

### 2. 기존 REST API (선택사항)

```bash
# 터미널 2: 기존 REST API (병렬 운영 가능)
uvicorn app.main:app --port 8080 --reload
```

### 3. A2A Host Agent (멀티 에이전트 오케스트레이션)

```bash
# 터미널 3: Agent1 실행
uvicorn a2a-poc.agents.agent1:a2a_app --port 8001

# 터미널 4: Agent2 실행
uvicorn a2a-poc.agents.agent2:a2a_app --port 8002

# 터미널 5: Host Agent (모든 에이전트 조율)
python -m a2a-poc.host.agent_with_ticker
```

## A2A Agent 기능

### 1. calculate_ticker_score

주식 티커의 점수를 계산합니다.

**요청:**
```json
{
  "ticker": "AAPL"
}
```

**응답:**
```json
{
  "ticker": "AAPL",
  "score": 78,
  "rationale": "AI 산업 성장 기대감과 분석가의 긍정적 평가...",
  "price": {
    "ticker": "AAPL",
    "last": 150.25,
    "chg": 2.5,
    "pct": 1.69
  },
  "news": [
    {
      "title": "Apple announces new product",
      "summary": "...",
      "url": "https://..."
    }
  ],
  "filings": [...]
}
```

### 2. get_ticker_info

에이전트 정보 및 사용 가능한 기능을 반환합니다.

**응답:**
```json
{
  "agent": "Ticker Score Agent",
  "description": "금융 데이터와 뉴스를 분석하여 주식 종목의 투자 점수(0-100)를 산출합니다",
  "capabilities": [
    "Yahoo Finance 주가 데이터 수집 (MCP)",
    "뉴스 감성 분석",
    "DART 공시 정보 수집",
    "LLM 기반 종합 점수 산출"
  ],
  "example_tickers": ["AAPL", "MSFT", "NVDA", "TSLA", "GOOGL", "005930.KS"]
}
```

## A2A 통신 흐름

```
외부 에이전트/Host
    ↓
[HTTP POST] /.well-known/agent-card.json
    ↓ (에이전트 능력 확인)
    ↓
[HTTP POST] /a2a/execute
    ↓ {skill: "calculate_ticker_score", args: {ticker: "AAPL"}}
    ↓
ticker_agent (포트 8083)
    ↓ calculate_ticker_score 호출
    ↓
LangGraph 워크플로우 실행
    ├─ ingest: 티커 추출
    ├─ yahoo: Yahoo Finance (MCP)
    ├─ dart: 공시 데이터
    ├─ score: LLM 점수 산출
    └─ finalize: 결과 정리
    ↓
JSON 응답 반환
    ↓
외부 에이전트/Host
```

## Host Agent 사용 예시

Host Agent를 통해 여러 에이전트를 조율:

```python
# 주식 분석 요청
"AAPL 주식을 분석해줘"
→ ticker_score_agent로 transfer
→ {"ticker": "AAPL", "score": 78, "rationale": "..."}

# 포트폴리오 분석
"AAPL, MSFT, NVDA 포트폴리오를 분석해줘"
→ 각 티커마다 ticker_score_agent로 transfer
→ 3개 결과를 종합하여 포트폴리오 평가

# 에이전트 소개
"사용 가능한 에이전트들을 소개해줘"
→ agent1_remote, agent2_remote, ticker_score_agent로 각각 transfer
→ 모든 에이전트의 소개를 종합
```

## 장점

1. **기존 코드 재사용**: LangGraph 워크플로우를 그대로 활용
2. **독립적 운영**: REST API(8080)와 A2A 서버(8083) 병렬 운영
3. **표준 프로토콜**: A2A 표준으로 다른 에이전트와 통신
4. **확장성**: 추가 툴을 쉽게 추가 가능

## 트러블슈팅

### google-adk import 오류
```bash
pip install google-adk
```

### MCP 서버 연결 오류
`mcp_config.json`에서 Yahoo Finance MCP 서버 경로를 확인하세요.

### 포트 충돌
각 에이전트는 서로 다른 포트에서 실행해야 합니다:
- REST API: 8080
- Agent1: 8001
- Agent2: 8002
- Ticker Agent: 8083
- Host: 8000

## 참고

- [Google ADK Documentation](https://github.com/google/adk)
- [A2A Protocol Specification](https://github.com/google/a2a-protocol)
