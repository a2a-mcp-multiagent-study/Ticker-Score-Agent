# 1) 원격 A2A 에이전트 2개를 "하위 에이전트"로 연결
import os
from typing import Dict, Any, Optional

from google.adk.models.lite_llm import LiteLlm

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
# ✅ 정확한 카드 URL (루트/.well-known)
AGENT1_CARD = "http://127.0.0.1:8001/.well-known/agent-card.json"
AGENT2_CARD = "http://127.0.0.1:8002/.well-known/agent-card.json"

agent1_remote = RemoteA2aAgent(
    name="agent1_remote",
    description="A2A remote Agent1",
    agent_card=f"http://127.0.0.1:8001{AGENT_CARD_WELL_KNOWN_PATH}",
)
agent2_remote = RemoteA2aAgent(
    name="agent2_remote",
    description="A2A remote Agent2",
    agent_card=f"http://127.0.0.1:8002{AGENT_CARD_WELL_KNOWN_PATH}",
)


# 2) Host가 제공하는 단일 툴: 두 에이전트를 호출해 결과를 합쳐줌
# def introduce_all(payload: Optional[Dict[str, Any]] = None, *, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
#     """
#     두 원격 에이전트에게 각자의 introduce 툴을 호출하고 결과를 합쳐 반환.
#     ADK의 RemoteA2aAgent는 내부적으로 A2A 프로토콜로 호출합니다.
#     """
#     # RemoteA2aAgent는 하위 에이전트처럼 취급되므로 transfer_to_agent_tool 없이,
#     # 하위 에이전트의 tool을 직접 지정해서 호출할 수 있도록 래핑되어 있습니다.
#     res1 = agent1_remote.invoke_tool("introduce", {})  # 동기 API (간단화를 위해)
#     res2 = agent2_remote.invoke_tool("introduce", {})
#     # 결과 합치기
#     return {
#         "agent1": res1,
#         "agent2": res2,
#         "combined_text": f"Agent1: {res1.get('intro')} | Agent2: {res2.get('intro')}",
#     }

# --- ADK 에이전트: Tools로 expose ---------------------------------------------
# root_agent = Agent(
#     name="host",
#     description="OpenAI 플래너로 자연어를 받아 필요시 introduce_all 툴을 호출하는 호스트",
#     tools=[chat, introduce_all],
#     sub_agents=[agent1_remote, agent2_remote],
# )

# root_agent = LlmAgent(
#     name="host",
#     description="두 원격 에이전트로 transfer하여 introduce를 실행하고 결과를 합쳐서 응답",
#     model=LiteLlm(model="openai/gpt-4o"),  # 또는 문서에 나온 Gemini 문자열
#     # 🔻 system_prompt 대신 instruction 사용
#     instruction=(
#         "사용자가 에이전트 소개를 원하면 agent1_remote와 agent2_remote로 transfer하여 "
#         "'introduce' 툴을 각각 실행하고 응답의 'intro'만 추출해 "
#         "'Agent1: ... | Agent2: ...' 한 줄로 합쳐서 답해라. "
#         "한쪽이 실패하면 가능한 쪽만 사용해라."
#     ),
#     tools=[],  # 함수툴 없다면 비워두기
#     sub_agents=[agent1_remote, agent2_remote],
# )


def introduce_all(input: Optional[Dict[str, Any]] = None, *, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    input = input or {}
    """LLM에게 두 원격 에이전트로 transfer 하라고 지시하는 신호 역할용.
       (직접 HTTP로 툴을 치지 않는다)"""
    # 이 함수는 “사용자 요청 → LLM → transfer 2회 → 응답 합치기” 흐름 중
    # LLM이 최종 결과를 이 포맷으로 내도록 유도할 때 쓰는 래퍼
    return {"ok": True, "note": "LLM이 agent1/agent2로 transfer 후 결과를 합쳐 반환해야 합니다."}

root_agent = LlmAgent(
    name="host",
    description="두 A2A 원격 에이전트에서 소개를 받아 합치는 호스트",
    # 모델은 ADK가 인식하는 키를 사용. (OpenAI는 LiteLlm로 래핑)
    model=LiteLlm(model="openai/gpt-4o"),  # 또는 "gemini-2.0-flash"
    instruction=(
        "먼저 반드시 두 번의 transfer(tool 'introduce', args {} 각각)를 끝내고 "
        "그 결과를 바탕으로 마지막에만 로컬 도구를 호출해 최종 JSON을 만들어라. "
        "중간에 로컬 도구를 호출하거나, 한 번의 transfer 후 종료하지 마라."
        "사용자가 소개를 원하면 반드시 순서대로:\n"
        "1) agent1_remote 로 transfer 하여 'introduce' 스킬을 호출해 JSON을 받는다.\n"
        "2) agent2_remote 로 transfer 하여 'introduce' 스킬을 호출해 JSON을 받는다.\n"
        "3) 최종으로 {agent1: <JSON>, agent2: <JSON>, combined_text: 'Agent1: ... | Agent2: ...'} 포맷의 JSON만 출력한다.\n"
        "원격 호출 오류 시 해당 에이전트 값은 {error: <메시지>}로 채우고 combined_text에는 'N/A'를 넣어라."
    ),
    tools=[introduce_all],  # 함수툴
    sub_agents=[agent1_remote, agent2_remote],
)