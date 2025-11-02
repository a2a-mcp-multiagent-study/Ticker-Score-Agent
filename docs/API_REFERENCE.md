# API 레퍼런스

Ticker-Score-Agent의 모든 API 엔드포인트와 사용법입니다.

## 📡 REST API (포트 8080)

일반적인 HTTP 요청을 통한 API입니다.

### Base URL

```
http://localhost:8080
```

---

## Endpoints

### 1. GET /score

티커 심볼의 투자 점수를 조회합니다.

#### Request

```http
GET /score?ticker={TICKER}
```

**Query Parameters:**

| 파라미터 | 타입 | 필수 | 설명 | 예시 |
|---------|------|------|------|------|
| ticker | string | ✅ | 주식 티커 심볼 | AAPL, MSFT, 005930.KS |

#### Response

**Status:** 200 OK

```json
{
  "ticker": "AAPL",
  "score": 78,
  "rationale": "AI 산업 성장 기대감과 분석가의 긍정적 평가 우세하나, 내부자 매도로 인한 경계감 상존"
}
```

**Response Fields:**

| 필드 | 타입 | 설명 |
|------|------|------|
| ticker | string | 조회한 티커 심볼 |
| score | integer | 투자 점수 (0-100) |
| rationale | string | 점수 산출 근거 |

#### Example

```bash
# cURL
curl "http://localhost:8080/score?ticker=AAPL"

# Python
import requests
response = requests.get("http://localhost:8080/score", params={"ticker": "AAPL"})
print(response.json())

# JavaScript
fetch("http://localhost:8080/score?ticker=AAPL")
  .then(res => res.json())
  .then(data => console.log(data));
```

---

### 2. GET /score/stream

Server-Sent Events(SSE)를 통한 스트리밍 방식 점수 조회입니다.

#### Request

```http
GET /score/stream?ticker={TICKER}
```

**Query Parameters:**

| 파라미터 | 타입 | 필수 | 설명 |
|---------|------|------|------|
| ticker | string | ✅ | 주식 티커 심볼 |

#### Response

**Status:** 200 OK
**Content-Type:** text/event-stream

```
event: progress
data: {"node": "ingest", "message": "티커 검증 중..."}

event: progress
data: {"node": "yahoo", "message": "Yahoo Finance 데이터 수집 중..."}

event: progress
data: {"node": "dart", "message": "DART 공시 정보 수집 중..."}

event: progress
data: {"node": "score", "message": "점수 산출 중..."}

event: done
data: {"ticker": "AAPL"}
```

#### Example

```bash
# cURL
curl -N "http://localhost:8080/score/stream?ticker=MSFT"

# Python
import requests
response = requests.get("http://localhost:8080/score/stream?ticker=MSFT", stream=True)
for line in response.iter_lines():
    if line:
        print(line.decode('utf-8'))

# JavaScript (EventSource)
const eventSource = new EventSource("http://localhost:8080/score/stream?ticker=MSFT");

eventSource.addEventListener("progress", (event) => {
  const data = JSON.parse(event.data);
  console.log(`Node: ${data.node}, Message: ${data.message}`);
});

eventSource.addEventListener("done", (event) => {
  console.log("Complete:", event.data);
  eventSource.close();
});
```

---

### 3. GET /score/trace

워크플로우 추적 정보를 포함한 점수 조회입니다.

#### Request

```http
GET /score/trace?ticker={TICKER}
```

**Query Parameters:**

| 파라미터 | 타입 | 필수 | 설명 |
|---------|------|------|------|
| ticker | string | ✅ | 주식 티커 심볼 |

#### Response

**Status:** 200 OK
**Content-Type:** text/event-stream

```
event: node_start
data: {"node": "ingest", "timestamp": "2025-11-02T12:00:00Z"}

event: node_end
data: {"node": "ingest", "timestamp": "2025-11-02T12:00:01Z", "output": {...}}

event: node_start
data: {"node": "yahoo", "timestamp": "2025-11-02T12:00:01Z"}

...

event: done
data: {"ticker": "AAPL", "score": 78, "rationale": "..."}
```

#### Example

```bash
# cURL
curl -N "http://localhost:8080/score/trace?ticker=NVDA"
```

---

## 🔗 A2A Protocol API (포트 8083)

Agent-to-Agent 프로토콜을 통한 에이전트 간 통신입니다.

### Base URL

```
http://localhost:8083
```

---

## A2A Endpoints

### 1. GET /.well-known/agent-card.json

에이전트의 능력과 메타데이터를 반환합니다.

#### Request

```http
GET /.well-known/agent-card.json
```

#### Response

**Status:** 200 OK

```json
{
  "name": "ticker_score_agent",
  "version": "0.0.1",
  "description": "금융 데이터와 뉴스를 분석하여 주식 종목의 투자 점수(0-100)를 산출하는 에이전트",
  "protocolVersion": "0.3.0",
  "preferredTransport": "JSONRPC",
  "url": "http://localhost:8083",
  "capabilities": {},
  "defaultInputModes": ["text/plain"],
  "defaultOutputModes": ["text/plain"],
  "supportsAuthenticatedExtendedCard": false,
  "skills": [
    {
      "id": "ticker_score_agent",
      "name": "model",
      "description": "...",
      "tags": ["llm"]
    },
    {
      "id": "ticker_score_agent-calculate_ticker_score",
      "name": "calculate_ticker_score",
      "description": "주식 티커의 점수를 계산합니다.",
      "tags": ["llm", "tools"]
    },
    {
      "id": "ticker_score_agent-get_ticker_info",
      "name": "get_ticker_info",
      "description": "에이전트 정보 및 사용 가능한 티커 예시를 반환합니다.",
      "tags": ["llm", "tools"]
    }
  ]
}
```

#### Example

```bash
# cURL
curl http://localhost:8083/.well-known/agent-card.json | python -m json.tool

# Python
import requests
response = requests.get("http://localhost:8083/.well-known/agent-card.json")
print(response.json())
```

---

### 2. POST /a2a/execute

A2A 프로토콜을 통해 에이전트를 실행합니다.

#### Request

```http
POST /a2a/execute
Content-Type: application/json
```

**Request Body (JSON-RPC 2.0):**

```json
{
  "jsonrpc": "2.0",
  "id": "1",
  "method": "execute",
  "params": {
    "skill": "calculate_ticker_score",
    "input": {
      "ticker": "AAPL"
    }
  }
}
```

#### Response

**Status:** 200 OK

```json
{
  "jsonrpc": "2.0",
  "id": "1",
  "result": {
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
        "title": "...",
        "summary": "...",
        "url": "..."
      }
    ],
    "filings": [...]
  }
}
```

#### Example

```bash
# cURL - A2A Protocol (JSON-RPC 2.0)
curl -X POST http://localhost:8083/ \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": "1",
    "method": "message/send",
    "params": {
      "message": {
        "kind": "message",
        "message_id": "msg-1",
        "role": "user",
        "parts": [
          {
            "kind": "text",
            "text": "Calculate the score for MSFT"
          }
        ]
      }
    }
  }'

# Python
import requests

payload = {
    "jsonrpc": "2.0",
    "id": "1",
    "method": "message/send",
    "params": {
        "message": {
            "kind": "message",
            "message_id": "msg-1",
            "role": "user",
            "parts": [
                {
                    "kind": "text",
                    "text": "Calculate the score for MSFT"
                }
            ]
        }
    }
}

response = requests.post(
    "http://localhost:8083/",
    json=payload,
    timeout=60
)

# 응답에서 결과 추출
result = response.json()
if "result" in result and "history" in result["result"]:
    for msg in result["result"]["history"]:
        if msg.get("role") == "agent" and "parts" in msg:
            for part in msg["parts"]:
                if part.get("kind") == "data" and "response" in part.get("data", {}):
                    data = part["data"]["response"]
                    if "ticker" in data:
                        print(f"Ticker: {data['ticker']}")
                        print(f"Score: {data['score']}/100")
                        print(f"Rationale: {data['rationale']}")
```

**Note**: The A2A protocol uses JSON-RPC 2.0 with `message/send` method at the root endpoint (`/`), not at `/a2a/execute`. The agent receives natural language prompts and responds with structured data in the task history.

---

## 🛠️ A2A Skills

### calculate_ticker_score

주식 티커의 점수를 계산합니다.

**Input:**
```json
{
  "ticker": "AAPL"
}
```

**Output:**
```json
{
  "ticker": "AAPL",
  "score": 78,
  "rationale": "...",
  "price": {...},
  "news": [...],
  "filings": [...]
}
```

### get_ticker_info

에이전트 정보를 조회합니다.

**Input:**
```json
{}
```

**Output:**
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
  "example_tickers": ["AAPL", "MSFT", "NVDA", "TSLA", "GOOGL", "005930.KS"],
  "usage": "calculate_ticker_score 툴을 호출하여 ticker 파라미터를 전달하세요"
}
```

---

## 🚨 에러 응답

### REST API 에러

```json
{
  "detail": "Error message here"
}
```

**Common HTTP Status Codes:**
- `400 Bad Request` - 잘못된 요청 파라미터
- `404 Not Found` - 엔드포인트를 찾을 수 없음
- `500 Internal Server Error` - 서버 내부 오류

### A2A 에러

```json
{
  "jsonrpc": "2.0",
  "id": "1",
  "error": {
    "code": -32600,
    "message": "Invalid Request"
  }
}
```

**JSON-RPC Error Codes:**
- `-32700` Parse error
- `-32600` Invalid Request
- `-32601` Method not found
- `-32602` Invalid params
- `-32603` Internal error

---

## 📊 Rate Limiting

현재 Rate Limiting이 구현되어 있지 않습니다. 프로덕션 환경에서는 적절한 Rate Limiting 설정을 권장합니다.

**권장 설정:**
- REST API: 100 requests/minute
- A2A API: 50 requests/minute

---

## 🔐 인증

현재 인증이 구현되어 있지 않습니다. 프로덕션 환경에서는 API Key 또는 OAuth를 추가하세요.

---

## 다음 단계

- [A2A 배포 가이드](./A2A_DEPLOYMENT.md)에서 멀티 에이전트 오케스트레이션 설정
- [트러블슈팅](./TROUBLESHOOTING.md)에서 일반적인 문제 해결
