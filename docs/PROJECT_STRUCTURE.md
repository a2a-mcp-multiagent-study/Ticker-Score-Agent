# 프로젝트 구조

Ticker-Score-Agent의 전체 프로젝트 구조와 각 컴포넌트에 대한 상세 설명입니다.

## 📁 디렉토리 구조

```
Ticker-Score-Agent/
├── app/                          # 메인 애플리케이션
│   ├── main.py                  # FastAPI REST API 서버
│   ├── a2a_server.py            # A2A 프로토콜 서버
│   ├── settings.py              # 환경 설정
│   └── workflow/                # LangGraph 워크플로우
│       ├── graph.py            # 워크플로우 그래프 정의
│       ├── nodes.py            # 워크플로우 노드 구현
│       ├── state.py            # 상태 정의
│       ├── llm.py              # LLM 클라이언트
│       ├── prompts.py          # 프롬프트 템플릿
│       ├── mcp_clients.py      # MCP 클라이언트
│       ├── trace.py            # 추적 기능
│       └── a2a_agent.py        # A2A 에이전트 래퍼
│
├── a2a-poc/                     # A2A 개념 증명
│   ├── agents/                 # 샘플 A2A 에이전트
│   │   ├── agent1.py
│   │   └── agent2.py
│   └── host/                   # 호스트 에이전트
│       ├── agent.py
│       └── agent_with_ticker.py
│
├── docs/                        # 문서
│   ├── README.md
│   ├── PROJECT_STRUCTURE.md
│   ├── GETTING_STARTED.md
│   ├── API_REFERENCE.md
│   ├── A2A_DEPLOYMENT.md
│   └── TROUBLESHOOTING.md
│
├── .env.example                 # 환경 변수 예시
├── .env                         # 환경 변수 (gitignore)
├── mcp_config.json             # MCP 서버 설정
├── langgraph.json              # LangGraph 설정
├── requirements.txt            # Python 의존성
├── README.md                   # 프로젝트 개요
├── A2A_SETUP.md               # A2A 설정 가이드
└── PR_DESCRIPTION.md          # PR 설명
```

## 🔧 핵심 컴포넌트

### 1. REST API 서버 (`app/main.py`)

일반적인 HTTP 요청을 처리하는 FastAPI 서버입니다.

**주요 엔드포인트:**
- `GET /score?ticker={TICKER}` - 티커 점수 조회
- `GET /score/stream?ticker={TICKER}` - 스트리밍 방식 점수 조회
- `GET /score/trace?ticker={TICKER}` - 추적 정보 포함 조회

**특징:**
- 동기/비동기 처리 지원
- SSE(Server-Sent Events) 스트리밍
- LangGraph 워크플로우 실행

### 2. A2A 서버 (`app/a2a_server.py`)

A2A 프로토콜을 통해 다른 에이전트와 통신하는 서버입니다.

**주요 엔드포인트:**
- `GET /.well-known/agent-card.json` - 에이전트 능력 정보
- `POST /a2a/execute` - A2A 프로토콜 실행

**특징:**
- Google ADK 기반
- `to_a2a()` 함수로 기존 Agent를 A2A 서버로 변환
- JSON-RPC 프로토콜 지원

### 3. LangGraph 워크플로우 (`app/workflow/`)

주식 점수 산출의 핵심 로직이 구현된 워크플로우입니다.

#### 3.1 그래프 정의 (`graph.py`)

```python
# 워크플로우 실행 함수
async def run_once(ticker: str) -> dict
async def run_stream(ticker: str) -> AsyncIterator
async def run_with_trace(ticker: str) -> AsyncIterator
```

**워크플로우 노드:**
1. `ingest` - 티커 입력 처리
2. `yahoo` - Yahoo Finance 데이터 수집 (MCP)
3. `dart` - DART 공시 데이터 수집
4. `score` - LLM 기반 점수 산출
5. `finalize` - 결과 정리

#### 3.2 노드 구현 (`nodes.py`)

각 워크플로우 단계의 실제 구현:

```python
async def node_ingest(state: TickerState) -> dict
async def node_yahoo(state: TickerState) -> dict
async def node_dart(state: TickerState) -> dict
async def node_score(state: TickerState) -> dict
async def node_finalize(state: TickerState) -> dict
```

#### 3.3 상태 관리 (`state.py`)

워크플로우 상태를 정의하는 TypedDict:

```python
class TickerState(TypedDict):
    ticker: str
    price: Optional[dict]
    news: Optional[list]
    filings: Optional[list]
    score: Optional[int]
    rationale: Optional[str]
```

#### 3.4 LLM 클라이언트 (`llm.py`)

다양한 LLM 제공자를 지원:
- OpenAI GPT-4
- Naver CLOVA X
- 기타 LangChain 호환 모델

#### 3.5 MCP 클라이언트 (`mcp_clients.py`)

Yahoo Finance MCP 서버와 통신:

```python
async def call_yahoo_price(ticker: str) -> dict
async def call_yahoo_news(ticker: str) -> list
```

### 4. A2A 에이전트 래퍼 (`app/workflow/a2a_agent.py`)

LangGraph 워크플로우를 Google ADK Agent로 래핑합니다.

**제공 도구:**
1. `calculate_ticker_score(input, context)` - 티커 점수 계산
2. `get_ticker_info(input, context)` - 에이전트 정보 조회

**Agent 정의:**
```python
ticker_agent = LlmAgent(
    name="ticker_score_agent",
    description="금융 데이터와 뉴스를 분석하여 주식 종목의 투자 점수(0-100)를 산출하는 에이전트",
    model=LiteLlm(model="openai/gpt-4o"),
    tools=[calculate_ticker_score, get_ticker_info],
)
```

### 5. 설정 파일

#### 5.1 환경 변수 (`.env`)

```bash
OPENAI_API_KEY=sk-...
NCP_CLOVASTUDIO_API_KEY=...
NCP_APIGW_API_KEY=...
DART_API_KEY=...
```

#### 5.2 MCP 설정 (`mcp_config.json`)

```json
{
  "mcpServers": {
    "yahoo-finance": {
      "command": "node",
      "args": ["/path/to/yahoo-finance-mcp/dist/index.js"],
      "env": {}
    }
  }
}
```

#### 5.3 LangGraph 설정 (`langgraph.json`)

```json
{
  "dependencies": ["."],
  "graphs": {
    "ticker_graph": "./app/workflow/graph.py:graph"
  },
  "env": ".env"
}
```

## 🔄 데이터 흐름

```
1. 사용자 요청 (ticker="AAPL")
   ↓
2. REST API or A2A 서버
   ↓
3. LangGraph 워크플로우 시작
   ↓
4. node_ingest: 티커 검증
   ↓
5. node_yahoo: MCP → Yahoo Finance
   ├─ 주가 데이터
   └─ 뉴스 데이터
   ↓
6. node_dart: DART API
   └─ 공시 정보
   ↓
7. node_score: LLM 분석
   └─ 점수 및 근거 산출
   ↓
8. node_finalize: 결과 정리
   ↓
9. JSON 응답 반환
```

## 🧩 의존성

### 주요 패키지

- **fastapi** (0.117.1) - 웹 서버 프레임워크
- **langgraph** (0.6.7) - 워크플로우 오케스트레이션
- **langchain** (0.3.27) - LLM 통합
- **mcp** (1.14.1) - Model Context Protocol
- **google-adk** (1.17.0) - Google Agent Development Kit
- **a2a-server** (0.6.1) - A2A 프로토콜 서버
- **a2a-sdk** (0.3.10) - A2A SDK

### 전체 의존성

`requirements.txt` 참조

## 📊 워크플로우 시각화

LangGraph Studio를 사용하여 워크플로우를 시각적으로 확인할 수 있습니다:

```bash
langgraph dev
```

브라우저에서 http://localhost:8123 접속

## 🔐 보안 고려사항

1. **API 키 관리**: `.env` 파일은 절대 커밋하지 마세요
2. **환경 분리**: 개발/운영 환경 분리
3. **Rate Limiting**: API 요청 제한 설정 권장
4. **인증**: 프로덕션 환경에서는 인증 추가 필요

## 다음 단계

- [시작 가이드](./GETTING_STARTED.md)에서 설치 및 실행 방법 확인
- [API 레퍼런스](./API_REFERENCE.md)에서 상세 API 스펙 확인
- [A2A 배포 가이드](./A2A_DEPLOYMENT.md)에서 A2A 서버 설정 확인
