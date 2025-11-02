# A2A 배포 가이드

Agent-to-Agent (A2A) 프로토콜 서버 설정 및 멀티 에이전트 오케스트레이션 가이드입니다.

## 📖 A2A 프로토콜이란?

A2A (Agent-to-Agent) 프로토콜은 Google이 제안한 에이전트 간 통신 표준 프로토콜입니다.

### 주요 특징

- **표준화된 통신**: JSON-RPC 기반 표준 프로토콜
- **에이전트 디스커버리**: Agent Card를 통한 능력 공개
- **유연한 통합**: 다양한 에이전트 간 상호운용성
- **확장 가능**: 새로운 스킬 추가 용이

### 아키텍처

```
┌─────────────────┐
│   Host Agent    │  ← 오케스트레이터
└────────┬────────┘
         │
    ┌────┴────┬────────┬────────┐
    │         │        │        │
┌───▼───┐ ┌──▼───┐ ┌──▼───┐ ┌──▼──────────┐
│Agent 1│ │Agent2│ │Agent3│ │Ticker Agent │
└───────┘ └──────┘ └──────┘ └─────────────┘
```

---

## 🚀 Ticker Score Agent를 A2A 서버로 실행

### 1. 기본 실행

```bash
# 프로젝트 루트에서 실행 (중요!)
cd /path/to/Ticker-Score-Agent

uvicorn app.a2a_server:a2a_app --reload --port 8083
```

### 2. 서버 확인

```bash
# Agent Card 확인
curl http://localhost:8083/.well-known/agent-card.json | python -m json.tool

# 기대 출력: 에이전트 메타데이터 및 스킬 목록
```

### 3. 제공되는 스킬

#### calculate_ticker_score

주식 티커의 투자 점수를 계산합니다.

**요청:**
```json
{
  "jsonrpc": "2.0",
  "id": "1",
  "method": "execute",
  "params": {
    "skill": "calculate_ticker_score",
    "input": {"ticker": "AAPL"}
  }
}
```

**응답:**
```json
{
  "jsonrpc": "2.0",
  "id": "1",
  "result": {
    "ticker": "AAPL",
    "score": 78,
    "rationale": "...",
    "price": {...},
    "news": [...],
    "filings": [...]
  }
}
```

#### get_ticker_info

에이전트 정보 및 사용 가능한 티커 예시를 반환합니다.

**요청:**
```json
{
  "jsonrpc": "2.0",
  "id": "2",
  "method": "execute",
  "params": {
    "skill": "get_ticker_info",
    "input": {}
  }
}
```

---

## 🎭 멀티 에이전트 오케스트레이션

여러 에이전트를 조율하여 복잡한 작업을 수행할 수 있습니다.

### 아키텍처 예시

```
a2a-poc/
├── agents/
│   ├── agent1.py          # 자기소개 에이전트
│   └── agent2.py          # 날씨 정보 에이전트
└── host/
    ├── agent.py           # 기본 호스트
    └── agent_with_ticker.py  # Ticker Agent 포함 호스트
```

### 1. 샘플 에이전트 실행

#### Agent 1 실행

```bash
cd /path/to/Ticker-Score-Agent/a2a-poc

# 가상 환경 활성화 (a2a-poc용)
source .venv/bin/activate

# Agent 1 실행
uvicorn agents.agent1:a2a_app --port 8001
```

**Agent 1 능력:**
- 자기소개 (introduce)

#### Agent 2 실행

```bash
# 새 터미널
cd /path/to/Ticker-Score-Agent/a2a-poc
source .venv/bin/activate

# Agent 2 실행
uvicorn agents.agent2:a2a_app --port 8002
```

**Agent 2 능력:**
- 날씨 정보 제공 (weather)

#### Ticker Agent 실행

```bash
# 새 터미널
cd /path/to/Ticker-Score-Agent

# 메인 프로젝트 가상 환경 활성화
source app/.venv/bin/activate

# Ticker Agent 실행
uvicorn app.a2a_server:a2a_app --port 8083
```

**Ticker Agent 능력:**
- 티커 점수 계산 (calculate_ticker_score)
- 에이전트 정보 (get_ticker_info)

### 2. Host Agent 실행

Host Agent는 모든 에이전트를 조율합니다.

```bash
cd /path/to/Ticker-Score-Agent/a2a-poc
source .venv/bin/activate

# Ticker Agent를 포함하는 Host Agent 실행
python -m host.agent_with_ticker
```

### 3. 사용 예시

Host Agent가 실행되면 대화형 인터페이스가 시작됩니다.

```
User: AAPL 주식을 분석해줘

Host Agent:
→ ticker_score_agent로 전달
→ {"ticker": "AAPL", "score": 78, "rationale": "..."}
→ 결과 종합 및 응답
```

```
User: 에이전트들을 소개해줘

Host Agent:
→ agent1_remote로 전달 → "나는 Agent 1입니다"
→ agent2_remote로 전달 → "나는 Agent 2입니다"
→ ticker_score_agent로 전달 → {...}
→ 모든 에이전트 소개 종합
```

---

## 🛠️ 커스텀 A2A 에이전트 만들기

### 1. 기본 에이전트 구조

```python
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from typing import Dict, Any, Optional

# 1. 툴 함수 정의
def my_tool(input: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    내 커스텀 툴입니다.
    """
    # 로직 구현
    result = {"message": "Hello from my tool!"}
    return result

# 2. Agent 정의
my_agent = LlmAgent(
    name="my_agent",
    description="나만의 에이전트입니다",
    model=LiteLlm(model="openai/gpt-4o"),
    tools=[my_tool],
)

# 3. A2A 서버로 변환
a2a_app = to_a2a(my_agent, port=8084)
```

### 2. 비동기 툴 사용

```python
async def async_tool(input: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    비동기 툴 예시
    """
    import asyncio
    await asyncio.sleep(1)  # 비동기 작업

    return {"result": "Async operation completed"}

my_agent = LlmAgent(
    name="async_agent",
    description="비동기 에이전트",
    model=LiteLlm(model="openai/gpt-4o"),
    tools=[async_tool],
)

a2a_app = to_a2a(my_agent, port=8085)
```

### 3. LangGraph 워크플로우 래핑

Ticker Score Agent처럼 기존 LangGraph 워크플로우를 A2A로 래핑할 수 있습니다.

```python
from app.workflow.graph import run_once

async def execute_workflow(input: Dict[str, Any], context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    LangGraph 워크플로우를 실행합니다.
    """
    param = input.get("param")

    # 기존 워크플로우 실행
    result = await run_once(param)

    return result

workflow_agent = LlmAgent(
    name="workflow_agent",
    description="워크플로우 실행 에이전트",
    model=LiteLlm(model="openai/gpt-4o"),
    tools=[execute_workflow],
)

a2a_app = to_a2a(workflow_agent, port=8086)
```

---

## 🌐 Host Agent 설정

Host Agent는 여러 Remote Agent를 조율합니다.

### 1. Remote Agent 등록

```python
from google.adk.a2a.agents.remote_a2a_agent import RemoteA2aAgent

# Remote Agent 생성
ticker_agent_remote = RemoteA2aAgent(
    url="http://localhost:8083",
    name="ticker_score_agent",
)

agent1_remote = RemoteA2aAgent(
    url="http://localhost:8001",
    name="agent1",
)

agent2_remote = RemoteA2aAgent(
    url="http://localhost:8002",
    name="agent2",
)
```

### 2. Host Agent에 등록

```python
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

host_agent = LlmAgent(
    name="host_agent",
    description="모든 에이전트를 조율하는 호스트 에이전트",
    model=LiteLlm(model="openai/gpt-4o"),
    instruction=(
        "당신은 여러 에이전트를 조율하는 호스트 에이전트입니다.\n"
        "사용자 요청에 따라 적절한 에이전트로 작업을 전달하세요.\n\n"
        "- 주식 분석 요청 → ticker_score_agent\n"
        "- 소개 요청 → agent1_remote\n"
        "- 날씨 정보 → agent2_remote\n"
    ),
    agents=[ticker_agent_remote, agent1_remote, agent2_remote],
)
```

### 3. Host Agent 실행

```python
from google.adk.runners import Runner

runner = Runner(host_agent)

# 대화형 실행
runner.run_chat()

# 또는 단일 실행
result = runner.run("AAPL 주식을 분석해줘")
print(result)
```

---

## 🔧 고급 설정

### 1. Agent Card 커스터마이징

```python
from google.adk.a2a.utils.agent_to_a2a import to_a2a

a2a_app = to_a2a(
    agent=my_agent,
    port=8084,
    agent_card_config={
        "version": "1.0.0",
        "capabilities": {
            "streaming": True,
            "batch": False,
        },
        "metadata": {
            "author": "Your Name",
            "license": "MIT",
        }
    }
)
```

### 2. 인증 추가

```python
from fastapi import Security, HTTPException
from fastapi.security.api_key import APIKeyHeader

API_KEY = "your-secret-key"
api_key_header = APIKeyHeader(name="X-API-Key")

def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(status_code=403, detail="Invalid API Key")
    return api_key

# FastAPI 앱에 의존성 추가
a2a_app.dependency_overrides[verify_api_key] = lambda: API_KEY
```

### 3. CORS 설정

```python
from fastapi.middleware.cors import CORSMiddleware

a2a_app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📊 모니터링 및 로깅

### 1. OpenTelemetry 통합

Google ADK는 OpenTelemetry를 기본 지원합니다.

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)

logger = logging.getLogger("my-a2a-agent")
```

### 2. 메트릭 수집

```bash
# Prometheus 엔드포인트
curl http://localhost:8083/metrics
```

---

## 🚀 프로덕션 배포

### 1. Docker Compose 사용

```yaml
version: '3.8'

services:
  ticker-agent:
    build: .
    ports:
      - "8083:8083"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    command: uvicorn app.a2a_server:a2a_app --host 0.0.0.0 --port 8083

  agent1:
    build: ./a2a-poc
    ports:
      - "8001:8001"
    command: uvicorn agents.agent1:a2a_app --host 0.0.0.0 --port 8001

  agent2:
    build: ./a2a-poc
    ports:
      - "8002:8002"
    command: uvicorn agents.agent2:a2a_app --host 0.0.0.0 --port 8002

  host:
    build: ./a2a-poc
    depends_on:
      - ticker-agent
      - agent1
      - agent2
    command: python -m host.agent_with_ticker
```

### 2. 실행

```bash
docker-compose up -d
```

---

## 🔍 디버깅

### Agent Card 확인

```bash
# 모든 에이전트의 Agent Card 확인
curl http://localhost:8001/.well-known/agent-card.json
curl http://localhost:8002/.well-known/agent-card.json
curl http://localhost:8083/.well-known/agent-card.json
```

### 연결 테스트

```python
from google.adk.a2a.agents.remote_a2a_agent import RemoteA2aAgent

# Remote Agent 생성
agent = RemoteA2aAgent(url="http://localhost:8083", name="ticker_score_agent")

# 연결 테스트
print(agent.get_agent_card())
```

---

## 다음 단계

- [API 레퍼런스](./API_REFERENCE.md)에서 A2A API 상세 스펙 확인
- [트러블슈팅](./TROUBLESHOOTING.md)에서 일반적인 문제 해결
- [Google ADK 문서](https://github.com/google/adk)에서 더 많은 예시 확인
