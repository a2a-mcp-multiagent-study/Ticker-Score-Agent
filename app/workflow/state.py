# app/workflow/state.py
from __future__ import annotations
from typing import Any, Dict, List, Optional, TypedDict

from langchain_core.messages import AnyMessage
from langgraph.graph import add_messages
from typing_extensions import Annotated
import operator

class ScoreState(TypedDict, total=False):
    ticker: str
    price: Optional[Dict[str, Any]]
    news: Optional[List[Dict[str, Any]]]
    filings: Optional[List[Dict[str, Any]]]
    score: Optional[int]
    rationale: Optional[str]
    # 병렬 합치기: 리스트 이어붙이기
    logs: Annotated[List[str], operator.add]
    # ✅ Chat 탭용: LangGraph가 자동으로 Human/AI 메시지를 누적
    messages: Annotated[List[AnyMessage], add_messages]
    # (선택) 폼 입력 지원용 텍스트 필드
    text: Optional[str]
