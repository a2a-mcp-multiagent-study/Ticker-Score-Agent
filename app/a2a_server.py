"""
A2A Server for Ticker Score Agent
Google ADK의 to_a2a()를 사용하여 Agent를 A2A 프로토콜 서버로 변환
"""
import logging

from app.workflow.a2a_agent import root_agent

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)
logger = logging.getLogger("ticker-a2a-server")

try:
    from google.adk.a2a.utils.agent_to_a2a import to_a2a
except ImportError as e:
    logger.error("google-adk not installed. Install with: pip install google-adk")
    raise RuntimeError("google-adk is required for A2A server") from e


# A2A FastAPI 앱 생성
# - /.well-known/agent-card.json: 에이전트 능력 정보
# - /: A2A 프로토콜 JSON-RPC 엔드포인트 (method: message/send)
a2a_app = to_a2a(root_agent, port=8083)

logger.info("Ticker Score Agent A2A server initialized on port 8083")
logger.info("Agent Card: http://localhost:8083/.well-known/agent-card.json")
logger.info("JSON-RPC endpoint: http://localhost:8083/ (method: message/send)")

# 실행 방법:
# uvicorn app.a2a_server:a2a_app --port 8083 --reload
