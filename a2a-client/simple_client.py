#!/usr/bin/env python3
"""
Simple A2A Client - HTTP 직접 호출

가장 간단한 방법으로 A2A 서버와 통신합니다.
requests 라이브러리만 사용하여 JSON-RPC 요청을 보냅니다.

사용법:
    python simple_client.py
"""

import requests
import json
from typing import Dict, Any


# A2A 서버 URL
SERVER_URL = "http://localhost:8083"


def call_a2a_skill(skill: str, input_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    A2A 스킬을 호출합니다.

    Args:
        skill: 스킬 이름 (예: "calculate_ticker_score")
        input_data: 입력 데이터 (예: {"ticker": "AAPL"})

    Returns:
        스킬 실행 결과
    """
    # 티커를 자연어 프롬프트로 변환
    ticker = input_data.get("ticker", "")
    prompt = f"Calculate the score for {ticker}" if ticker else "Get agent info"

    # JSON-RPC 2.0 요청 구성 (A2A 프로토콜)
    payload = {
        "jsonrpc": "2.0",
        "id": "1",
        "method": "message/send",
        "params": {
            "message": {
                "kind": "message",
                "message_id": "msg-1",
                "role": "user",
                "parts": [
                    {
                        "kind": "text",
                        "text": prompt
                    }
                ]
            }
        }
    }

    # A2A 서버로 요청 (루트 엔드포인트)
    url = f"{SERVER_URL}/"

    try:
        response = requests.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=60  # 60초 타임아웃
        )
        response.raise_for_status()

        # 응답 파싱
        result = response.json()

        # 에러 체크
        if "error" in result:
            print(f"❌ 에러 발생: {result['error']}")
            return None

        # A2A 응답에서 데이터 추출
        response_data = result.get("result", {})

        # history에서 function_response 찾기
        if "history" in response_data:
            for msg in response_data["history"]:
                if msg.get("role") == "agent" and "parts" in msg:
                    for part in msg["parts"]:
                        if part.get("kind") == "data":
                            data = part.get("data", {})
                            if "response" in data and isinstance(data["response"], dict):
                                # calculate_ticker_score의 응답 반환
                                if "ticker" in data["response"]:
                                    return data["response"]

        # artifacts에서 텍스트 응답 추출 (폴백)
        if "artifacts" in response_data:
            for artifact in response_data["artifacts"]:
                if "parts" in artifact:
                    for part in artifact["parts"]:
                        if part.get("kind") == "text":
                            return {"raw_response": part.get("text", "")}

        return response_data

    except requests.exceptions.ConnectionError:
        print(f"❌ 연결 실패: {SERVER_URL}")
        print("A2A 서버가 실행 중인지 확인하세요.")
        print("실행 방법: uvicorn app.a2a_server:a2a_app --reload --port 8083")
        return None

    except requests.exceptions.Timeout:
        print("❌ 타임아웃: 요청 시간이 초과되었습니다.")
        return None

    except Exception as e:
        print(f"❌ 예외 발생: {e}")
        return None


def get_agent_card() -> Dict[str, Any]:
    """
    Agent Card를 조회합니다.

    Returns:
        에이전트 메타데이터
    """
    url = f"{SERVER_URL}/.well-known/agent-card.json"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"❌ Agent Card 조회 실패: {e}")
        return None


def calculate_ticker_score(ticker: str):
    """티커 점수를 계산합니다."""
    print(f"\n{'='*60}")
    print(f"📊 티커 점수 계산: {ticker}")
    print(f"{'='*60}\n")

    result = call_a2a_skill(
        skill="calculate_ticker_score",
        input_data={"ticker": ticker}
    )

    if result:
        print(f"✅ 티커: {result.get('ticker')}")
        print(f"📈 점수: {result.get('score')}/100")
        print(f"💡 근거: {result.get('rationale')}")

        # 추가 정보
        if result.get('price'):
            price = result['price']
            print(f"\n💰 주가 정보:")
            print(f"   현재가: ${price.get('last')}")
            print(f"   변동: {price.get('chg')} ({price.get('pct')}%)")

        if result.get('news'):
            print(f"\n📰 뉴스: {len(result['news'])}건")

        print(f"\n{'='*60}\n")
        return result

    return None


def get_agent_info():
    """에이전트 정보를 조회합니다."""
    print(f"\n{'='*60}")
    print(f"ℹ️  에이전트 정보 조회")
    print(f"{'='*60}\n")

    result = call_a2a_skill(
        skill="get_ticker_info",
        input_data={}
    )

    if result:
        print(f"🤖 에이전트: {result.get('agent')}")
        print(f"📝 설명: {result.get('description')}")
        print(f"\n✨ 기능:")
        for capability in result.get('capabilities', []):
            print(f"   • {capability}")
        print(f"\n📊 예시 티커:")
        print(f"   {', '.join(result.get('example_tickers', []))}")
        print(f"\n{'='*60}\n")
        return result

    return None


def main():
    """메인 함수"""
    print("🚀 Simple A2A Client")
    print("=" * 60)

    # 1. Agent Card 확인
    print("\n1️⃣ Agent Card 확인 중...")
    agent_card = get_agent_card()
    if agent_card:
        print(f"✅ 에이전트 이름: {agent_card.get('name')}")
        print(f"✅ 프로토콜 버전: {agent_card.get('protocolVersion')}")
        print(f"✅ 스킬 개수: {len(agent_card.get('skills', []))}")
    else:
        print("❌ Agent Card 조회 실패")
        return

    # 2. 에이전트 정보 조회
    print("\n2️⃣ 에이전트 정보 조회 중...")
    get_agent_info()

    # 3. 티커 점수 계산
    print("3️⃣ 티커 점수 계산 중...")

    # 예시 1: AAPL
    calculate_ticker_score("AAPL")

    # 예시 2: MSFT (주석 해제하여 사용)
    # calculate_ticker_score("MSFT")

    # 예시 3: 여러 티커 비교
    # tickers = ["AAPL", "MSFT", "NVDA"]
    # print(f"\n📊 포트폴리오 분석: {', '.join(tickers)}")
    # results = []
    # for ticker in tickers:
    #     result = calculate_ticker_score(ticker)
    #     if result:
    #         results.append(result)
    #
    # # 평균 점수 계산
    # if results:
    #     avg_score = sum(r.get('score', 0) for r in results) / len(results)
    #     print(f"\n평균 점수: {avg_score:.1f}/100")

    print("✨ 완료!")


if __name__ == "__main__":
    main()
