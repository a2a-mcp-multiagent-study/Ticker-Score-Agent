# 트러블슈팅

Ticker-Score-Agent 사용 시 발생할 수 있는 일반적인 문제와 해결 방법입니다.

## 🔍 일반적인 문제

### 1. 서버 실행 오류

#### 문제: `ModuleNotFoundError: No module named 'app'`

```
Traceback (most recent call last):
  ...
ModuleNotFoundError: No module named 'app'
```

**원인:** 잘못된 디렉토리에서 실행

**해결:**
```bash
# ❌ 잘못된 방법 (app 디렉토리 안에서)
cd app
uvicorn main:app --port 8080

# ✅ 올바른 방법 (프로젝트 루트에서)
cd /path/to/Ticker-Score-Agent
uvicorn app.main:app --port 8080
```

#### 문제: `ModuleNotFoundError: No module named 'workflow'`

```
ModuleNotFoundError: No module named 'workflow'
```

**원인:** Import 경로 문제

**해결:**
파일에서 상대 경로(`workflow.`)를 절대 경로(`app.workflow.`)로 수정:

```python
# ❌ 잘못된 방법
from workflow.graph import run_once

# ✅ 올바른 방법
from app.workflow.graph import run_once
```

---

### 2. 의존성 설치 오류

#### 문제: `pip install` 실패

```
ERROR: Could not find a version that satisfies the requirement...
```

**해결:**

```bash
# 1. pip 업그레이드
pip install --upgrade pip

# 2. Python 버전 확인 (3.10+ 필요)
python --version

# 3. 가상 환경 재생성
rm -rf app/.venv
python -m venv app/.venv
source app/.venv/bin/activate
pip install -r requirements.txt
```

#### 문제: `google-adk` 관련 오류

```
ModuleNotFoundError: No module named 'a2a'
```

**해결:**

```bash
# 1. google-adk 버전 확인
pip show google-adk

# 2. 필요 시 업그레이드
pip install --upgrade google-adk

# 3. a2a-sdk 설치
pip install a2a-server a2a-sdk a2a-json-rpc

# 4. 추가 의존성 설치
pip install aiofiles deprecated litellm
```

---

### 3. MCP 연결 오류

#### 문제: Yahoo Finance MCP 서버 연결 실패

```
Error: Cannot connect to MCP server
```

**해결:**

1. **MCP 서버 경로 확인**

```bash
# mcp_config.json 확인
cat mcp_config.json
```

절대 경로를 사용하세요:
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

2. **Yahoo Finance MCP 서버 빌드 확인**

```bash
cd /path/to/yahoo-finance-mcp

# 의존성 설치
npm install

# 빌드
npm run build

# dist/index.js 파일 확인
ls -la dist/index.js
```

3. **Node.js 버전 확인**

```bash
# Node.js 18 이상 필요
node --version
```

#### 문제: `mcp_config.json` 파일을 찾을 수 없음

**해결:**

```bash
# 프로젝트 루트에 mcp_config.json 생성
cd /path/to/Ticker-Score-Agent

cat > mcp_config.json << 'EOF'
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
EOF
```

---

### 4. API 키 오류

#### 문제: OpenAI API 키 오류

```
openai.error.AuthenticationError: Incorrect API key provided
```

**해결:**

1. **.env 파일 확인**

```bash
cat .env
```

2. **API 키 형식 확인**

```bash
# .env 파일
OPENAI_API_KEY=sk-proj-...  # ✅ 올바름
OPENAI_API_KEY="sk-proj-..."  # ❌ 따옴표 제거
```

3. **환경 변수 로드 확인**

```python
# Python에서 확인
import os
from dotenv import load_dotenv

load_dotenv()
print(os.getenv("OPENAI_API_KEY"))  # None이 아니어야 함
```

---

### 5. 포트 충돌

#### 문제: `Address already in use`

```
ERROR: [Errno 48] Address already in use
```

**해결:**

1. **사용 중인 프로세스 확인**

```bash
# macOS/Linux
lsof -ti:8080
lsof -ti:8083

# Windows
netstat -ano | findstr :8080
```

2. **프로세스 종료**

```bash
# macOS/Linux
kill -9 $(lsof -ti:8080)

# Windows (관리자 권한)
taskkill /PID <PID> /F
```

3. **다른 포트 사용**

```bash
uvicorn app.main:app --port 8081
uvicorn app.a2a_server:a2a_app --port 8084
```

---

### 6. A2A 서버 오류

#### 문제: Agent Card를 찾을 수 없음

```
404 Not Found: /.well-known/agent-card.json
```

**해결:**

1. **서버 로그 확인**

서버 시작 시 다음 로그가 표시되어야 합니다:
```
INFO ticker-a2a-server: Ticker Score Agent A2A server initialized on port 8083
INFO ticker-a2a-server: Agent Card: http://localhost:8083/.well-known/agent-card.json
```

2. **서버 재시작**

```bash
# 프로세스 종료
kill -9 $(lsof -ti:8083)

# 재시작
cd /path/to/Ticker-Score-Agent
uvicorn app.a2a_server:a2a_app --reload --port 8083
```

#### 문제: `RuntimeError: google-adk is required for A2A server`

**해결:**

```bash
# google-adk 및 관련 패키지 설치
pip install --upgrade google-adk
pip install a2a-server a2a-sdk a2a-json-rpc
pip install litellm deprecated aiofiles
```

---

### 7. LangGraph 워크플로우 오류

#### 문제: 워크플로우 실행 중 오류

```
Error in node 'yahoo': ...
```

**해결:**

1. **로그 확인**

```bash
# 상세 로그로 실행
uvicorn app.main:app --log-level debug
```

2. **각 노드 개별 테스트**

```python
# Python 셸에서
from app.workflow.nodes import node_yahoo
from app.workflow.state import TickerState

state = TickerState(ticker="AAPL")
result = await node_yahoo(state)
print(result)
```

---

### 8. LLM 응답 오류

#### 문제: LLM이 응답하지 않음

```
Timeout error: LLM did not respond
```

**해결:**

1. **API 상태 확인**

```bash
# OpenAI API 상태
curl https://status.openai.com/api/v2/status.json
```

2. **타임아웃 설정 증가**

```python
# app/workflow/llm.py
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-4o",
    timeout=60,  # 60초로 증가
    max_retries=3,
)
```

3. **다른 모델 사용**

```python
# gpt-4o-mini로 변경 (더 빠름)
llm = ChatOpenAI(model="gpt-4o-mini")
```

---

## 🐛 디버깅 팁

### 1. 로그 레벨 조정

```bash
# 상세 로그
export LOG_LEVEL=DEBUG
uvicorn app.main:app --log-level debug

# 최소 로그
export LOG_LEVEL=WARNING
uvicorn app.main:app --log-level warning
```

### 2. Python 디버거 사용

```python
# 코드에 브레이크포인트 추가
import pdb; pdb.set_trace()

# 또는 IPython
import IPython; IPython.embed()
```

### 3. 환경 변수 확인

```bash
# 모든 환경 변수 출력
printenv | grep -E "(OPENAI|NCP|DART)"
```

### 4. 의존성 버전 확인

```bash
# 설치된 패키지 버전 확인
pip list | grep -E "(fastapi|langgraph|langchain|google-adk|mcp)"

# requirements.txt와 비교
pip check
```

---

## 📊 성능 문제

### 1. 느린 응답 시간

**원인:**
- Yahoo Finance MCP 서버 응답 지연
- DART API 응답 지연
- LLM 처리 시간

**해결:**

1. **스트리밍 API 사용**

```bash
# 일반 API 대신 스트리밍 사용
curl "http://localhost:8080/score/stream?ticker=AAPL"
```

2. **캐싱 추가**

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_ticker_data(ticker: str):
    # 캐싱된 데이터 반환
    pass
```

3. **병렬 처리**

```python
import asyncio

# 여러 노드를 병렬로 실행
results = await asyncio.gather(
    node_yahoo(state),
    node_dart(state),
)
```

### 2. 메모리 사용량 증가

**해결:**

```bash
# 워커 프로세스 수 제한
uvicorn app.main:app --workers 2

# 메모리 사용량 모니터링
ps aux | grep uvicorn
```

---

## 🔐 보안 문제

### 1. API 키 노출

**확인:**
```bash
# .env 파일이 커밋되지 않았는지 확인
git status

# .gitignore에 포함되어 있는지 확인
cat .gitignore | grep .env
```

**해결:**
```bash
# .gitignore에 추가
echo ".env" >> .gitignore

# 이미 커밋된 경우
git rm --cached .env
git commit -m "Remove .env from tracking"
```

---

## 🆘 추가 지원

### 문제가 해결되지 않나요?

1. **로그 수집**
```bash
uvicorn app.main:app --log-level debug > debug.log 2>&1
```

2. **환경 정보 수집**
```bash
python --version
pip list > packages.txt
printenv > env.txt
```

3. **GitHub Issues**
- 로그 파일 첨부
- 환경 정보 포함
- 재현 단계 설명

### 유용한 리소스

- [LangChain 문서](https://python.langchain.com/)
- [LangGraph 문서](https://langchain-ai.github.io/langgraph/)
- [FastAPI 문서](https://fastapi.tiangolo.com/)
- [Google ADK GitHub](https://github.com/google/adk)
- [MCP 공식 문서](https://modelcontextprotocol.io/)

---

## 📝 문제 보고 템플릿

```markdown
### 환경
- OS: macOS / Linux / Windows
- Python 버전:
- 설치 방법: pip / conda

### 문제 설명
[문제를 상세히 설명해주세요]

### 재현 단계
1.
2.
3.

### 예상 동작
[기대했던 동작]

### 실제 동작
[실제 발생한 동작]

### 로그
```
[로그 붙여넣기]
```

### 시도한 해결 방법
[이미 시도해본 방법들]
```

---

이 문서에서 해결되지 않는 문제가 있다면 GitHub Issues에 문의해주세요!
