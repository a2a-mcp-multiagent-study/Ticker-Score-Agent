# 1) 순수 ADK Agent 정의 (툴 한 개: introduce)
from typing import Dict, Any, Optional

from google.adk import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a
from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools import FunctionTool


def introduce(_ : Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    # 단순 JSON 결과; A2A 응답 payload가 됨
    return {"intro": "나는 Agent 1 입니다.", "who": "agent-1"}

# agent1 = Agent(
#     name="agent1",
#     description="자기소개를 반환하는 간단한 원격 에이전트",
#     tools=[introduce],   # 이름 자동 추출: "introduce"
# )

agent1 = LlmAgent(
    name="agent1",
    description="자기소개를 반환하는 간단한 원격 에이전트",
    model=LiteLlm(model="openai/gpt-4o"),   # ← ★ 모델 지정
    tools=[introduce],                      # 함수만 넣으면 자동 래핑
)

# 2) A2A 서버 앱으로 래핑 (FastAPI 앱 반환)
#   - 문서의 권장 방식 그대로: uvicorn으로 띄웁니다.
#   - 포트는 8001로 가정
a2a_app = to_a2a(agent1, port=8001)