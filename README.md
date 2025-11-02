# Ticker-Score-Agent
금융 데이터(MCP) + 뉴스 요약을 기반으로 점수를 산출하는 AGENT

<img width="491" alt="image" src="https://github.com/user-attachments/assets/4a5a1f22-d33d-4a74-a3ad-83956db721e5" />

## LangGraph Studio 
|Graph|Chat|
|-|-|
|<img width="377" alt="image" src="https://github.com/user-attachments/assets/fb3ec426-b46f-4c0c-b372-24af747c5802" />|<img width="568" alt="image" src="https://github.com/user-attachments/assets/0d0b8e31-c990-4fc3-97c7-d9478dcab6b6" />|

## A2A PoC 
|Graph|Chat|
|-|-|
|<img width="422" height="243" alt="image" src="https://github.com/user-attachments/assets/1dfacce7-3c7f-437d-8cfc-3f59e39a31e1" />|<img width="512" alt="image" src="https://github.com/user-attachments/assets/2af37292-5358-4f28-8673-604df346af2b" />|

## 📚 Documentation

상세한 문서는 [`docs/`](./docs/) 폴더를 참고하세요:

- **[시작 가이드](./docs/GETTING_STARTED.md)** - 설치부터 첫 실행까지
- **[프로젝트 구조](./docs/PROJECT_STRUCTURE.md)** - 전체 아키텍처 및 구성요소
- **[API 레퍼런스](./docs/API_REFERENCE.md)** - REST API 및 A2A 엔드포인트
- **[A2A 배포 가이드](./docs/A2A_DEPLOYMENT.md)** - 멀티 에이전트 설정
- **[트러블슈팅](./docs/TROUBLESHOOTING.md)** - 일반적인 문제 해결

## Quick Start

> [!IMPORTANT]
> Python 3.10+ is required. <br/>
> Yahoo Finance MCP Server is a required dependency. [:octocat: GitHub Repo](https://github.com/Alex2Yang97/yahoo-finance-mcp)<br/>
> You must configure `mcp_config.json` to register your MCP server. <br/>

```bash
# 1. 의존성 설치
pip install -r requirements.txt

# 2. 환경 변수 설정
cp .env.example .env
# .env 파일에 API 키 입력

# 3. MCP 설정
# mcp_config.json에 Yahoo Finance MCP 서버 경로 설정

# 4. REST API 서버 실행
uvicorn app.main:app --reload --port 8080
```

### Environment Variables

`.env` 파일은 [`app/settings.py`](./app/settings.py)에서 자동으로 로드됩니다. 최소한 아래 항목을 채워주세요.

| KEY | Required | Description |
| --- | --- | --- |
| `OPENAI_API_KEY` | ✅ | LangChain `ChatOpenAI` 호출용 API 키 |
| `CLOVASTUDIO_API_KEY` | ⛔️ (선택) | NAVER CLOVA Studio 를 사용할 경우 입력 |
| `MCP_CONFIG_PATH` | ✅ | `mcp_config.json` 절대/상대 경로 (`./mcp_config.json` 권장) |
| `LANGCHAIN_TRACING_V2`, `LANGCHAIN_API_KEY` | ⛔️ (선택) | LangSmith 추적을 사용할 경우 |

예시:

```bash
OPENAI_API_KEY=sk-proj-...
CLOVASTUDIO_API_KEY=nv-...
MCP_CONFIG_PATH=./mcp_config.json
```

### Yahoo Finance MCP Server

점수 산출은 MCP 서버에 의존합니다. [yahoo-finance-mcp](https://github.com/Alex2Yang97/yahoo-finance-mcp)를 설치 후 `mcp_config.json`에 경로를 등록하세요.

```bash
# 별도 디렉터리에서 MCP 서버 설치
git clone https://github.com/Alex2Yang97/yahoo-finance-mcp.git
cd yahoo-finance-mcp
npm install && npm run build

# 실행 경로 확인 (예: dist/index.js)
```

프로젝트 루트의 `mcp_config.json` 예시:

```json
{
  "mcpServers": {
    "yahoo-finance": {
      "command": "node",
      "args": ["/abs/path/yahoo-finance-mcp/dist/index.js"],
      "env": {}
    }
  }
}
```

> ℹ️ MCP 서버가 먼저 실행되어 있어야 `run_once` → Yahoo/DART 노드가 정상 동작합니다.

### Usage

```bash
# 티커 점수 조회
curl "http://localhost:8080/score?ticker=AAPL"
curl "http://localhost:8080/score?ticker=MSFT"

# 스트리밍 조회
curl "http://localhost:8080/score/stream?ticker=NVDA"
```

### Response Example

```json
{
  "ticker": "NVDA",
  "score": 78,
  "rationale": "AI 산업 성장 기대감과 분석가의 긍정적 평가 우세하나, 내부자 매도로 인한 경계감 상존"
}
```

## A2A Protocol Support

Ticker-Score-Agent는 A2A (Agent-to-Agent) 프로토콜을 지원하여 다른 에이전트와 통신할 수 있습니다.

### Features
- **Google ADK 기반**: LangGraph 워크플로우를 ADK Agent로 래핑
- **병렬 운영**: REST API (8080) + A2A 서버 (8083) 동시 실행
- **멀티 에이전트**: Host Agent를 통한 에이전트 오케스트레이션
- **표준 프로토콜**: A2A 표준으로 다른 에이전트와 통신

### Quick Start

```bash
# 프로젝트 루트에서 실행 (중요!)
cd /path/to/Ticker-Score-Agent

# A2A 서버 실행
uvicorn app.a2a_server:a2a_app --host 127.0.0.1 --port 8083 --reload

# Agent Card 확인
curl http://localhost:8083/.well-known/agent-card.json
```

> google-adk, a2a-server, a2a-sdk 등 A2A 관련 패키지는 최상위 `requirements.txt`에 포함되어 있습니다. `pip install -r requirements.txt`만 실행하면 추가 설치가 필요 없습니다.

멀티 에이전트 PoC(`a2a-poc/`)를 체험하려면 Agent1/2를 각각 띄운 뒤 [`a2a-poc/host/agent.py`](./a2a-poc/host/agent.py)에 있는 Host Agent를 실행하세요.

### Available Tools
- `calculate_ticker_score`: 주식 티커 점수 산출
- `get_ticker_info`: 에이전트 정보 조회

### 상세 문서
- **[A2A 배포 가이드](./docs/A2A_DEPLOYMENT.md)** - 멀티 에이전트 오케스트레이션
- **[A2A 설정 가이드](./A2A_SETUP.md)** - 기본 A2A 설정
- **[API 레퍼런스](./docs/API_REFERENCE.md)** - A2A 프로토콜 API
