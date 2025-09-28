# Ticker-Score-Agent
금융 데이터(MCP) + 뉴스 요약을 기반으로 점수를 산출하는 AGENT

<img width="491" alt="image" src="https://github.com/user-attachments/assets/4a5a1f22-d33d-4a74-a3ad-83956db721e5" />

## LangGraph Studio 
|Graph|Chat|
|-|-|
|<img width="377" alt="image" src="https://github.com/user-attachments/assets/fb3ec426-b46f-4c0c-b372-24af747c5802" />|<img width="568" alt="image" src="https://github.com/user-attachments/assets/0d0b8e31-c990-4fc3-97c7-d9478dcab6b6" />|

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
