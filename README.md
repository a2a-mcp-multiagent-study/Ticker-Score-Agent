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
|<img width="422" height="243" alt="image" src="https://github.com/user-attachments/assets/1dfacce7-3c7f-437d-8cfc-3f59e39a31e1" />|<img width="512" alt="image" src="https://github.com/user-attachments/assets/2af37292-5358-4f28-8673-604df346af2b" />
|

## Setup
> [!IMPORTANT]
> Python 3.10+ is required. <br/>
> Yahoo Finance MCP Server is a required dependency. [:octocat: GitHub Repo](https://github.com/Alex2Yang97/yahoo-finance-mcp)<br/>
> You must configure `mcp_config.json` to register your MCP server. <br/>

```bash
pip install -r requirements.txt

# run fastapi server
uvicorn app.main:app --reload --port 8080 
```

## Usage
```bash
curl "http://localhost:8080/score?ticker=MSFT"
curl "http://localhost:8080/score?ticker=NVDA"
```

## Result
```json
{
  "ticker":"NVDA",
  "score":78,
  "rationale":"AI 산업 성장 기대감과 분석가의 긍정적 평가 우세하나, 내부자 매도로 인한 경계감 상존"
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
# A2A 서버 실행
uvicorn app.a2a_server:a2a_app --port 8083 --reload

# Agent Card 확인
curl http://localhost:8083/.well-known/agent-card.json
```

### Available Tools
- `calculate_ticker_score`: 주식 티커 점수 산출
- `get_ticker_info`: 에이전트 정보 조회

자세한 내용은 [A2A_SETUP.md](./A2A_SETUP.md)를 참고하세요.
