from typing import Dict, Any, Optional

from google.adk.agents import Agent, LlmAgent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.function_tool import FunctionTool
from google.adk.a2a.utils.agent_to_a2a import to_a2a


def introduce(_ : Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    return {"intro": "나는 Agent 3 입니다.", "who": "agent-3"}

# agent2 = Agent(
#     name="agent2",
#     description="자기소개를 반환하는 간단한 원격 에이전트",
#     tools=[introduce],
# )

agent2 = LlmAgent(
    name="agent2",
    description="자기소개를 반환하는 간단한 원격 에이전트",
    model=LiteLlm(model="openai/gpt-4o"),   # ← ★ 모델 지정
    tools=[introduce],                      # 함수만 넣으면 자동 래핑
)

a2a_app = to_a2a(agent2, port=8003)