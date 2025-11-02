#!/usr/bin/env python3
"""
A2A SDK Client - ClientFactory 사용

a2a-sdk의 ClientFactory를 사용하여 A2A 서버와 통신합니다.
표준 A2A 프로토콜을 따르는 깔끔한 코드입니다.

사용법:
    python adk_client.py
"""

import asyncio
from typing import Dict, Any

try:
    from a2a.client import ClientFactory
    from a2a.types import Message, TextPart
except ImportError:
    print("❌ a2a-sdk가 설치되지 않았습니다.")
    print("설치: pip install a2a-sdk")
    exit(1)


# A2A 서버 URL
SERVER_URL = "http://localhost:8083"


class TickerScoreClient:
    """
    Ticker Score Agent A2A 클라이언트
    """

    def __init__(self, server_url: str = SERVER_URL):
        """
        클라이언트 초기화

        Args:
            server_url: A2A 서버 URL
        """
        self.server_url = server_url
        self.client = None
        self.card = None

    async def connect(self):
        """A2A 서버에 연결"""
        try:
            self.client = await ClientFactory.connect(self.server_url)
            self.card = await self.client.get_card()
            print(f"✅ A2A 에이전트 연결 성공: {self.server_url}")
            return True
        except Exception as e:
            print(f"❌ A2A 에이전트 연결 실패: {e}")
            print(f"서버가 {self.server_url}에서 실행 중인지 확인하세요.")
            return False

    async def get_agent_card(self) -> Dict[str, Any]:
        """
        Agent Card를 조회합니다.

        Returns:
            에이전트 메타데이터
        """
        try:
            if not self.card:
                self.card = await self.client.get_card()
            return self.card
        except Exception as e:
            print(f"❌ Agent Card 조회 실패: {e}")
            return {}

    async def calculate_ticker_score(self, ticker: str) -> Dict[str, Any]:
        """
        티커 점수를 계산합니다.

        Args:
            ticker: 티커 심볼 (예: "AAPL", "MSFT")

        Returns:
            점수 계산 결과
        """
        try:
            # A2A 메시지 생성
            message = Message(
                kind="message",
                message_id=f"msg-{ticker}",
                role="user",
                parts=[
                    TextPart(
                        kind="text",
                        text=f"Calculate the score for {ticker}"
                    )
                ]
            )

            # 메시지 전송 및 응답 수집
            result = None
            async for item in self.client.send_message(message):
                # Task와 업데이트 이벤트 처리
                if isinstance(item, tuple):
                    task, update = item
                    # 완료된 태스크에서 결과 추출
                    if task.status.state == "completed" and task.history:
                        # history에서 function_response 찾기
                        for msg in task.history:
                            if msg.role == "agent" and msg.parts:
                                for part in msg.parts:
                                    if part.kind == "data" and hasattr(part, 'data'):
                                        data = part.data
                                        if hasattr(data, 'response') and isinstance(data.response, dict):
                                            if "ticker" in data.response:
                                                result = data.response
                                                break
                # Message 응답 처리
                elif hasattr(item, 'parts'):
                    for part in item.parts:
                        if part.kind == "text":
                            result = {"raw_response": part.text}

            return result if result else {}

        except Exception as e:
            print(f"❌ 티커 점수 계산 실패: {e}")
            import traceback
            traceback.print_exc()
            return {}

    async def get_agent_info(self) -> Dict[str, Any]:
        """
        에이전트 정보를 조회합니다.

        Returns:
            에이전트 정보
        """
        try:
            message = Message(
                kind="message",
                message_id="msg-info",
                role="user",
                parts=[
                    TextPart(
                        kind="text",
                        text="Get agent info"
                    )
                ]
            )

            result = None
            async for item in self.client.send_message(message):
                if isinstance(item, tuple):
                    task, update = item
                    if task.status.state == "completed" and task.history:
                        for msg in task.history:
                            if msg.role == "agent" and msg.parts:
                                for part in msg.parts:
                                    if part.kind == "data" and hasattr(part, 'data'):
                                        data = part.data
                                        if hasattr(data, 'response'):
                                            result = data.response
                                            break

            return result if result else {}

        except Exception as e:
            print(f"❌ 에이전트 정보 조회 실패: {e}")
            return {}


def print_ticker_result(ticker: str, result: Dict[str, Any]):
    """티커 점수 결과를 출력합니다."""
    print(f"\n{'='*60}")
    print(f"📊 {ticker} 분석 결과")
    print(f"{'='*60}\n")

    if not result:
        print("❌ 결과 없음")
        return

    print(f"✅ 티커: {result.get('ticker')}")
    print(f"📈 점수: {result.get('score')}/100")
    print(f"💡 근거: {result.get('rationale')}")

    # 주가 정보
    if result.get('price'):
        price = result['price']
        print(f"\n💰 주가 정보:")
        print(f"   현재가: ${price.get('last')}")
        print(f"   변동: {price.get('chg')} ({price.get('pct')}%)")

    # 뉴스 정보
    if result.get('news'):
        print(f"\n📰 최신 뉴스: {len(result['news'])}건")
        for i, news in enumerate(result['news'][:3], 1):
            print(f"   {i}. {news.get('title', 'N/A')}")

    # 공시 정보
    if result.get('filings'):
        print(f"\n📑 공시 정보: {len(result['filings'])}건")

    print(f"\n{'='*60}\n")


def print_agent_info(info: Dict[str, Any]):
    """에이전트 정보를 출력합니다."""
    print(f"\n{'='*60}")
    print(f"ℹ️  에이전트 정보")
    print(f"{'='*60}\n")

    if not info:
        print("❌ 정보 없음")
        return

    print(f"🤖 에이전트: {info.get('agent')}")
    print(f"📝 설명: {info.get('description')}")

    print(f"\n✨ 주요 기능:")
    for capability in info.get('capabilities', []):
        print(f"   • {capability}")

    print(f"\n📊 지원 티커 예시:")
    print(f"   {', '.join(info.get('example_tickers', []))}")

    print(f"\n💡 사용법:")
    print(f"   {info.get('usage')}")

    print(f"\n{'='*60}\n")


async def main():
    """메인 함수"""
    print("🚀 A2A SDK Client")
    print("=" * 60)

    # 클라이언트 생성 및 연결
    client = TickerScoreClient()
    if not await client.connect():
        return

    # 1. Agent Card 확인
    print("\n1️⃣ Agent Card 확인 중...")
    agent_card = await client.get_agent_card()
    if agent_card:
        print(f"✅ 에이전트 이름: {agent_card.name}")
        print(f"✅ 프로토콜 버전: {agent_card.protocol_version}")
        print(f"✅ 스킬 개수: {len(agent_card.skills or [])}")
        print("\n스킬 목록:")
        for skill in (agent_card.skills or []):
            desc = (skill.description or 'N/A')[:50]
            print(f"   • {skill.name} - {desc}...")

    # 2. 에이전트 정보 조회
    print("\n2️⃣ 에이전트 정보 조회 중...")
    info = await client.get_agent_info()
    print_agent_info(info)

    # 3. 티커 점수 계산
    print("3️⃣ 티커 점수 계산 중...")

    # 예시 1: AAPL
    result = await client.calculate_ticker_score("AAPL")
    print_ticker_result("AAPL", result)

    print("✨ 완료!")


if __name__ == "__main__":
    asyncio.run(main())
