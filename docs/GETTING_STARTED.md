# 시작 가이드

Ticker-Score-Agent를 설치하고 실행하는 완전한 가이드입니다.

## 📋 사전 요구사항

### 필수 요구사항

- **Python**: 3.10 이상 (3.11 권장)
- **Node.js**: 18.0 이상 (Yahoo Finance MCP 서버용)
- **pip**: 최신 버전
- **Git**: 프로젝트 클론용

### API 키

다음 API 키가 필요합니다:

1. **OpenAI API Key** (필수)
   - https://platform.openai.com/api-keys
   - GPT-4 접근 권한 필요

2. **Naver CLOVA Studio API Key** (선택)
   - https://www.ncloud.com/product/aiService/clovaStudio
   - HyperCLOVA X 사용 시 필요

3. **DART API Key** (선택)
   - https://opendart.fss.or.kr/
   - 한국 상장사 공시 정보 사용 시 필요

## 🚀 설치

### 1. 프로젝트 클론

```bash
git clone <repository-url>
cd Ticker-Score-Agent
```

### 2. 가상 환경 생성 및 활성화

```bash
# 가상 환경 생성
python -m venv app/.venv

# 가상 환경 활성화
# macOS/Linux:
source app/.venv/bin/activate

# Windows:
app\.venv\Scripts\activate
```

### 3. 의존성 설치

```bash
pip install -r requirements.txt
```

**주요 의존성:**
- FastAPI
- LangChain & LangGraph
- OpenAI
- MCP (Model Context Protocol)
- Google ADK (Agent Development Kit)
- A2A Server & SDK

설치 시간: 약 3-5분

### 4. Yahoo Finance MCP 서버 설치

Yahoo Finance MCP 서버는 별도 설치가 필요합니다.

```bash
# 별도 디렉토리에서
git clone https://github.com/Alex2Yang97/yahoo-finance-mcp.git
cd yahoo-finance-mcp

# Node.js 패키지 설치
npm install

# 빌드
npm run build
```

### 5. 환경 변수 설정

```bash
# .env 파일 생성
cp .env.example .env
```

`.env` 파일 편집:

```bash
# OpenAI API Key (필수)
OPENAI_API_KEY=sk-proj-...

# Naver CLOVA Studio (선택)
NCP_CLOVASTUDIO_API_KEY=...
NCP_APIGW_API_KEY=...

# DART API (선택)
DART_API_KEY=...

# LangSmith 추적 (선택)
LANGCHAIN_TRACING_V2=false
LANGCHAIN_API_KEY=...
```

### 6. MCP 서버 설정

`mcp_config.json` 파일을 프로젝트 루트에 생성:

```json
{
  "mcpServers": {
    "yahoo-finance": {
      "command": "node",
      "args": [
        "/절대/경로/yahoo-finance-mcp/dist/index.js"
      ],
      "env": {}
    }
  }
}
```

**⚠️ 중요:** `args`에 Yahoo Finance MCP 서버의 **절대 경로**를 입력하세요.

예시:
```json
{
  "mcpServers": {
    "yahoo-finance": {
      "command": "node",
      "args": [
        "/Users/username/projects/yahoo-finance-mcp/dist/index.js"
      ],
      "env": {}
    }
  }
}
```

## 🏃 실행

### 방법 1: REST API 서버 실행

일반적인 HTTP API로 서비스를 제공합니다.

```bash
# 프로젝트 루트에서 실행 (중요!)
cd /path/to/Ticker-Score-Agent

uvicorn app.main:app --reload --port 8080
```

**서버 확인:**
```bash
# 브라우저에서
http://localhost:8080/docs

# curl로 테스트
curl "http://localhost:8080/score?ticker=AAPL"
```

**예상 출력:**
```json
{
  "ticker": "AAPL",
  "score": 78,
  "rationale": "AI 산업 성장 기대감과 분석가의 긍정적 평가..."
}
```

### 방법 2: A2A 서버 실행

A2A 프로토콜로 다른 에이전트와 통신합니다.

```bash
# 프로젝트 루트에서 실행 (중요!)
cd /path/to/Ticker-Score-Agent

uvicorn app.a2a_server:a2a_app --reload --port 8083
```

**서버 확인:**
```bash
# Agent Card 확인
curl http://localhost:8083/.well-known/agent-card.json

# 브라우저에서
http://localhost:8083/.well-known/agent-card.json
```

### 방법 3: 병렬 실행

두 서버를 동시에 실행할 수 있습니다.

```bash
# 터미널 1: REST API
uvicorn app.main:app --reload --port 8080

# 터미널 2: A2A 서버
uvicorn app.a2a_server:a2a_app --reload --port 8083
```

### 방법 4: LangGraph Studio (개발용)

LangGraph Studio를 사용하여 워크플로우를 시각적으로 디버깅할 수 있습니다.

```bash
# LangGraph CLI 설치 (별도)
pip install langgraph-cli

# Studio 실행
langgraph dev
```

브라우저에서 http://localhost:8123 접속

## ✅ 설치 확인

### 1. REST API 테스트

```bash
# 점수 조회
curl "http://localhost:8080/score?ticker=MSFT"

# 스트리밍 조회
curl "http://localhost:8080/score/stream?ticker=NVDA"

# 추적 정보 포함
curl "http://localhost:8080/score/trace?ticker=TSLA"
```

### 2. A2A 서버 테스트

```bash
# Agent Card 확인
curl http://localhost:8083/.well-known/agent-card.json | python -m json.tool

# 서버 응답 확인
# (A2A 프로토콜 요청은 별도 클라이언트 필요)
```

### 3. 상태 확인

서버가 정상적으로 시작되면 다음과 같은 로그를 볼 수 있습니다:

**REST API:**
```
INFO:     Uvicorn running on http://127.0.0.1:8080
INFO:     Application startup complete.
```

**A2A 서버:**
```
INFO ticker-a2a-server: Ticker Score Agent A2A server initialized on port 8083
INFO ticker-a2a-server: Agent Card: http://localhost:8083/.well-known/agent-card.json
INFO ticker-a2a-server: Execute endpoint: http://localhost:8083/a2a/execute
```

## 🎯 다음 단계

1. **API 탐색**: [API 레퍼런스](./API_REFERENCE.md)에서 모든 엔드포인트 확인
2. **A2A 통합**: [A2A 배포 가이드](./A2A_DEPLOYMENT.md)에서 멀티 에이전트 설정
3. **문제 해결**: [트러블슈팅](./TROUBLESHOOTING.md)에서 일반적인 문제 해결

## 💡 팁

### 개발 모드 vs 프로덕션 모드

**개발 모드:**
```bash
uvicorn app.main:app --reload --port 8080
```
- `--reload`: 코드 변경 시 자동 재시작
- 디버깅에 유용

**프로덕션 모드:**
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8080 --workers 4
```
- `--workers`: 멀티 프로세스 실행
- `--host 0.0.0.0`: 외부 접근 허용

### 로그 레벨 설정

```bash
# 상세 로그
uvicorn app.main:app --log-level debug

# 최소 로그
uvicorn app.main:app --log-level warning
```

### Docker 사용 (선택)

Docker를 사용하여 격리된 환경에서 실행할 수 있습니다.

```dockerfile
# Dockerfile 예시
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app ./app
COPY .env .
COPY mcp_config.json .

EXPOSE 8080

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
```

빌드 및 실행:
```bash
docker build -t ticker-score-agent .
docker run -p 8080:8080 ticker-score-agent
```

## 🆘 문제가 발생했나요?

[트러블슈팅 가이드](./TROUBLESHOOTING.md)를 참고하세요.

일반적인 문제:
- Import 에러 → 가상 환경 활성화 확인
- MCP 연결 실패 → `mcp_config.json` 경로 확인
- API 키 에러 → `.env` 파일 확인
- 포트 충돌 → 다른 포트 사용
