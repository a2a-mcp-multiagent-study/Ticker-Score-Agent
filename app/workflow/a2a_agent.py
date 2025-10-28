"""
ADK Agent wrapper for Ticker Score workflow.
LangGraph 워크플로우를 Google ADK Agent로 래핑하여 A2A 프로토콜 지원
"""
from __future__ import annotations
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

try:
    from google.adk.agents import LlmAgent
    from google.adk.models.lite_llm import LiteLlm
except ImportError as e:
    logger.error("google-adk not installed. Install with: pip install google-adk")
    raise RuntimeError("google-adk is required for A2A agent") from e

from app.workflow.graph import run_once


async def calculate_ticker_score(
    input: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    주식 티커의 점수를 계산합니다.

    이 함수는 LangGraph 워크플로우를 실행하여:
    1. Yahoo Finance에서 주가 및 뉴스 데이터 수집 (MCP)
    2. DART에서 공시 정보 수집
    3. LLM으로 종합 분석하여 0-100점 점수 산출

    Args:
        input: {"ticker": "AAPL", "MSFT", "NVDA" 등}
        context: A2A 컨텍스트 (선택사항)

    Returns:
        {
            "ticker": "AAPL",
            "score": 78,
            "rationale": "AI 산업 성장 기대감과 분석가의 긍정적 평가...",
            "price": {
                "ticker": "AAPL",
                "last": 150.25,
                "chg": 2.5,
                "pct": 1.69
            },
            "news": [
                {
                    "title": "...",
                    "summary": "...",
                    "url": "..."
                }
            ],
            "filings": [...]
        }
    """
    ticker = input.get("ticker")
    if not ticker:
        return {"error": "ticker parameter is required", "example": {"ticker": "AAPL"}}

    try:
        logger.info(f"[A2A] Calculating score for ticker: {ticker}")

        # 기존 LangGraph 워크플로우 실행
        result = await run_once(ticker)

        response = {
            "ticker": result["ticker"],
            "score": result.get("score"),
            "rationale": result.get("rationale"),
            "price": result.get("price"),
            "news": result.get("news"),
            "filings": result.get("filings"),
        }

        logger.info(f"[A2A] Score calculated successfully: {ticker} = {response.get('score')}")
        return response

    except Exception as e:
        logger.error(f"[A2A] Error calculating score for {ticker}: {e}")
        return {
            "error": str(e),
            "ticker": ticker,
            "score": None,
            "rationale": f"점수 계산 중 오류 발생: {str(e)}"
        }


def get_ticker_info(
    input: Dict[str, Any],
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    에이전트 정보 및 사용 가능한 티커 예시를 반환합니다.

    Args:
        input: 빈 딕셔너리 또는 None

    Returns:
        에이전트 설명 및 예시
    """
    return {
        "agent": "Ticker Score Agent",
        "description": "금융 데이터와 뉴스를 분석하여 주식 종목의 투자 점수(0-100)를 산출합니다",
        "capabilities": [
            "Yahoo Finance 주가 데이터 수집 (MCP)",
            "뉴스 감성 분석",
            "DART 공시 정보 수집",
            "LLM 기반 종합 점수 산출"
        ],
        "example_tickers": ["AAPL", "MSFT", "NVDA", "TSLA", "GOOGL", "005930.KS"],
        "usage": "calculate_ticker_score 툴을 호출하여 ticker 파라미터를 전달하세요"
    }


# ADK Agent 정의
ticker_agent = LlmAgent(
    name="ticker_score_agent",
    description="금융 데이터와 뉴스를 분석하여 주식 종목의 투자 점수(0-100)를 산출하는 에이전트",
    model=LiteLlm(model="openai/gpt-4o"),
    instruction=(
        "당신은 주식 투자 분석 전문 에이전트입니다. "
        "사용자가 주식 티커 심볼(예: AAPL, MSFT, NVDA)을 제공하면 "
        "calculate_ticker_score 툴을 호출하여 다음을 수행합니다:\n\n"
        "1. Yahoo Finance에서 실시간 주가 및 최신 뉴스 수집\n"
        "2. DART에서 공시 정보 수집\n"
        "3. AI 모델로 종합 분석하여 0-100점 투자 점수 산출\n"
        "4. 점수의 근거를 명확히 설명\n\n"
        "결과는 JSON 형식으로 제공되며, 점수와 함께 상세한 근거를 포함합니다. "
        "사용자가 에이전트 정보를 요청하면 get_ticker_info 툴을 사용하세요."
    ),
    tools=[calculate_ticker_score, get_ticker_info],
)
