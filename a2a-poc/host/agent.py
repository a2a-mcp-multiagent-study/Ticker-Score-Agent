"""
Host Agent with Ticker Score Agent integration
기존 agent1, agent2와 함께 ticker_score_agent를 서브 에이전트로 포함
"""
import os
from typing import Dict, Any, Optional

from google.adk.models.lite_llm import LiteLlm
from google.adk.tools import MCPToolset
from google.adk.tools.mcp_tool import StdioConnectionParams
from mcp import StdioServerParameters

try:
    from google.adk.agents import Agent, LlmAgent
    from google.adk.tools.function_tool import FunctionTool
    from google.adk.agents.remote_a2a_agent import RemoteA2aAgent, AGENT_CARD_WELL_KNOWN_PATH
except ImportError as e:
    raise RuntimeError("google-adk가 설치되지 않았거나 import 경로가 잘못됨") from e

# --- OpenAI (플래너) ----------------------------------------------------------
from openai import OpenAI
_oai = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# --- A2A 원격 에이전트 등록 ---------------------------------------------------
# Agent 1 & 2 (기존)
agent1_remote = RemoteA2aAgent(
    name="agent1_remote",
    description="자기소개를 반환하는 Agent1",
    agent_card=f"http://127.0.0.1:8001{AGENT_CARD_WELL_KNOWN_PATH}",
)
agent2_remote = RemoteA2aAgent(
    name="agent2_remote",
    description="자기소개를 반환하는 Agent2",
    agent_card=f"http://127.0.0.1:8002{AGENT_CARD_WELL_KNOWN_PATH}",
)
agent3_remote = RemoteA2aAgent(
    name="agent3_remote",
    description="A2A remote Agent3",
    agent_card=f"http://127.0.0.1:8003{AGENT_CARD_WELL_KNOWN_PATH}",
)
agent4_remote = RemoteA2aAgent(
    name="agent4_remote",
    description="A2A remote Agent4",
    agent_card=f"http://127.0.0.1:8004{AGENT_CARD_WELL_KNOWN_PATH}",
)

# Ticker Score Agent (신규 추가)
ticker_agent_remote = RemoteA2aAgent(
    name="ticker_score_agent",
    description="주식 티커의 투자 점수를 분석하는 금융 에이전트",
    agent_card=f"http://127.0.0.1:8083{AGENT_CARD_WELL_KNOWN_PATH}",
)


def analyze_portfolio(
    input: Optional[Dict[str, Any]] = None,
    *,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    포트폴리오 분석을 위한 가이드 함수.
    실제로는 LLM이 ticker_score_agent로 transfer 하도록 유도합니다.

    Args:
        input: {"tickers": ["AAPL", "MSFT", "NVDA"]}

    Returns:
        분석 가이드
    """
    tickers = (input or {}).get("tickers", [])
    return {
        "ok": True,
        "message": f"각 티커 {tickers}에 대해 ticker_score_agent로 transfer하여 점수를 받아오세요.",
        "note": "LLM이 각 티커마다 ticker_score_agent의 calculate_ticker_score 툴을 호출해야 합니다."
    }


# Host Agent 정의
root_agent = LlmAgent(
    name="financial_orchestrator",
    description="여러 금융 분석 에이전트를 조율하는 호스트 에이전트",
    model=LiteLlm(model="openai/gpt-4o"),
    instruction=(
        "당신은 여러 에이전트를 조율하는 금융 분석 코디네이터입니다.\n\n"

        "**주식 분석 요청 시:**\n"
        "1. 사용자가 특정 주식 티커(예: AAPL, MSFT)의 분석을 요청하면\n"
        "2. ticker_score_agent로 transfer하여 'calculate_ticker_score' 툴 호출\n"
        "3. 결과에는 점수, 근거, 주가, 뉴스 정보가 포함됩니다\n"
        "4. 여러 종목이면 각각 transfer하여 결과를 수집하세요\n\n"

        "**에이전트 소개 요청 시:**\n"
        "1. agent1_remote와 agent2_remote로 각각 transfer\n"
        "2. 'introduce' 툴을 호출하여 소개를 받으세요\n\n"

        "**포트폴리오 분석 요청 시:**\n"
        "1. 제공된 티커 목록의 각 종목을 ticker_score_agent로 분석\n"
        "2. 모든 결과를 종합하여 포트폴리오 전체 평가를 제공하세요\n\n"

        "항상 명확하고 구조화된 JSON 형식으로 응답하세요."
    ),
    tools=[analyze_portfolio],
    sub_agents=[agent1_remote, agent2_remote, ticker_agent_remote],
)
