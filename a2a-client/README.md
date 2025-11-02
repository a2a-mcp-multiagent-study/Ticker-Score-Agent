# A2A Client Examples

Ticker Score Agent와 통신하는 다양한 클라이언트 예시입니다.

## 📁 파일 구조

```
a2a-client/
├── README.md                 # 이 파일
├── simple_client.py         # HTTP 직접 호출 (가장 간단)
├── adk_client.py           # RemoteA2aAgent 사용 (권장)
├── interactive_client.py   # 대화형 클라이언트
└── requirements.txt        # 필요한 패키지
```

## 🚀 사전 준비

### 1. A2A 서버 실행

먼저 Ticker Score Agent A2A 서버를 실행해야 합니다.

```bash
# 프로젝트 루트에서
cd /path/to/Ticker-Score-Agent
uvicorn app.a2a_server:a2a_app --reload --port 8083
```

### 2. 패키지 설치

```bash
# a2a-client 디렉토리에서
cd a2a-client
pip install -r requirements.txt
```

---

## 📖 예시별 설명

### 1. simple_client.py - HTTP 직접 호출

**가장 간단한 방법!** requests 라이브러리로 직접 HTTP 요청을 보냅니다.

```bash
python simple_client.py
```

**장점:**
- 별도 라이브러리 불필요 (requests만)
- 이해하기 쉬움
- 빠른 테스트에 적합

**단점:**
- JSON-RPC 요청 수동 작성
- 에러 처리 직접 구현

---

### 2. adk_client.py - a2a-sdk ClientFactory

**a2a-sdk 사용!** ClientFactory로 표준 A2A 프로토콜로 연결합니다.

```bash
python adk_client.py
```

**장점:**
- Agent Card 자동 조회
- 표준 A2A 프로토콜 사용
- 비동기 지원
- 다른 A2A 에이전트와 통합 용이

**단점:**
- a2a-sdk 설치 필요
- 긴 작업(60초+)에서 타임아웃 이슈 있음 (실시간 주식 분석 시)
- 간단한 사용에는 simple_client.py 추천

---

### 3. interactive_client.py - 대화형 클라이언트 (권장)

**대화형 인터페이스!** 터미널에서 대화하듯 사용합니다.

```bash
python interactive_client.py
```

**기능:**
- 티커 점수 조회
- 에이전트 정보 조회
- 여러 티커 비교
- 종료: `exit` 또는 `quit` 입력

**장점:**
- 가장 직관적인 사용법
- HTTP 직접 호출로 안정적
- 의존성 최소 (requests만)
- 여러 티커 비교 기능

**사용 예시:**
```
> AAPL
티커: AAPL
점수: 78
근거: AI 산업 성장 기대감과 분석가의 긍정적 평가...

> info
[에이전트 정보 표시]

> AAPL MSFT NVDA
[3개 티커 비교 분석]
```

---

## 🎯 사용 예시

### 단일 티커 조회

```python
# simple_client.py 사용
python simple_client.py
# 또는
# adk_client.py 사용
python adk_client.py
```

### 대화형으로 사용

```bash
python interactive_client.py

> AAPL
> MSFT
> info
> exit
```

---

## 🔧 커스터마이징

### 서버 URL 변경

각 파일에서 URL을 수정하세요:

```python
# 기본값
SERVER_URL = "http://localhost:8083"

# 변경 예시
SERVER_URL = "http://your-server:8083"
```

### 타임아웃 설정

```python
# simple_client.py에서
response = requests.post(url, json=payload, timeout=30)  # 30초

# adk_client.py에서
# RemoteA2aAgent가 자동으로 관리
```

---

## 📊 비교

| 파일 | 난이도 | 의존성 | 추천 | 사용 시기 |
|------|--------|--------|------|-----------|
| **simple_client.py** | ⭐ 쉬움 | requests만 | ✅ | 빠른 테스트, API 이해 |
| **adk_client.py** | ⭐⭐⭐ 고급 | a2a-sdk | ⚠️ | 비동기 A2A 통합, 타임아웃 이슈 주의 |
| **interactive_client.py** | ⭐ 쉬움 | requests만 | ✅ | 대화형 사용, 일상적인 조회 |

---

## 🐛 트러블슈팅

### 연결 실패

```
ConnectionError: Failed to connect to localhost:8083
```

**해결:**
1. A2A 서버가 실행 중인지 확인
   ```bash
   curl http://localhost:8083/.well-known/agent-card.json
   ```

2. 포트 번호 확인
3. 방화벽 설정 확인

### Import 에러

```
ModuleNotFoundError: No module named 'a2a'
```

**해결:**
```bash
pip install a2a-sdk
```

### adk_client.py 타임아웃

adk_client.py는 긴 작업(주식 분석 등)에서 타임아웃이 발생할 수 있습니다.

**해결:**
- `simple_client.py` 또는 `interactive_client.py` 사용 (60초 타임아웃 설정됨)
- 또는 a2a-sdk의 ClientConfig에서 타임아웃 증가

---

## 💡 다음 단계

- 더 복잡한 워크플로우는 `../a2a-poc/host/agent_with_ticker.py` 참고
- 멀티 에이전트 오케스트레이션은 `../docs/A2A_DEPLOYMENT.md` 참고
