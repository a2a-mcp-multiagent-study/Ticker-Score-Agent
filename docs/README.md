# Ticker Score Agent - Documentation

주식 종목 투자 점수 산출 에이전트의 완전한 문서입니다.

## 📚 목차

1. **[프로젝트 구조](./PROJECT_STRUCTURE.md)** - 전체 프로젝트 구조 및 각 컴포넌트 설명
2. **[시작 가이드](./GETTING_STARTED.md)** - 설치부터 첫 실행까지
3. **[API 레퍼런스](./API_REFERENCE.md)** - REST API 및 A2A 엔드포인트
4. **[A2A 배포 가이드](./A2A_DEPLOYMENT.md)** - A2A 프로토콜 서버 설정 및 배포
5. **[트러블슈팅](./TROUBLESHOOTING.md)** - 일반적인 문제 해결

## 🎯 프로젝트 개요

Ticker-Score-Agent는 금융 데이터와 뉴스를 분석하여 주식 종목의 투자 점수(0-100)를 산출하는 AI 에이전트입니다.

### 주요 기능

- **Yahoo Finance 연동**: MCP(Model Context Protocol)를 통한 실시간 주가 및 뉴스 수집
- **DART 공시 분석**: 한국 상장사 공시 정보 수집
- **AI 기반 점수 산출**: LLM을 활용한 종합 분석 및 점수 산출
- **LangGraph 워크플로우**: 체계적인 데이터 처리 파이프라인
- **A2A 프로토콜 지원**: 다른 에이전트와의 통신 및 오케스트레이션

### 기술 스택

- **Framework**: FastAPI, LangGraph
- **AI/LLM**: LangChain, OpenAI, Naver CLOVA X
- **Protocol**: MCP (Model Context Protocol), A2A (Agent-to-Agent)
- **Deployment**: Google ADK, Uvicorn

## 🚀 빠른 시작

```bash
# 1. 저장소 클론 및 이동
cd Ticker-Score-Agent

# 2. 의존성 설치
pip install -r requirements.txt

# 3. 환경 변수 설정
cp .env.example .env
# .env 파일에 API 키 설정

# 4. MCP 서버 설정
# mcp_config.json에 Yahoo Finance MCP 서버 경로 설정

# 5. 서버 실행
uvicorn app.main:app --reload --port 8080
```

자세한 내용은 [시작 가이드](./GETTING_STARTED.md)를 참고하세요.

## 📖 추가 리소스

- [프로젝트 GitHub](https://github.com/Alex2Yang97/yahoo-finance-mcp)
- [MCP 공식 문서](https://modelcontextprotocol.io)
- [Google ADK 문서](https://github.com/google/adk)
- [A2A 프로토콜 스펙](https://github.com/google/a2a-protocol)

## 💬 문의 및 기여

이슈나 질문이 있으시면 GitHub Issues를 이용해 주세요.
