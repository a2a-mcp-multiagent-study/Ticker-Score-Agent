#!/usr/bin/env python3
"""
Interactive A2A Client - 대화형 클라이언트

터미널에서 대화하듯이 Ticker Score Agent와 통신할 수 있는 클라이언트입니다.

사용법:
    python interactive_client.py

명령어:
    <TICKER>        티커 점수 조회 (예: AAPL, MSFT)
    info            에이전트 정보 조회
    help            도움말
    exit, quit      종료
"""

import sys
import requests
import json
from typing import Dict, Any


# A2A 서버 URL
SERVER_URL = "http://localhost:8083"


class InteractiveClient:
    """대화형 A2A 클라이언트"""

    def __init__(self, server_url: str = SERVER_URL):
        """클라이언트 초기화"""
        self.server_url = server_url

        try:
            # Agent Card 확인
            response = requests.get(f"{server_url}/.well-known/agent-card.json", timeout=5)
            response.raise_for_status()
            print(f"✅ 연결됨: {server_url}\n")
        except Exception as e:
            print(f"❌ 연결 실패: {e}")
            print(f"서버가 {server_url}에서 실행 중인지 확인하세요.")
            raise

    def _call_a2a(self, prompt: str) -> Dict[str, Any]:
        """A2A 프로토콜로 메시지 전송"""
        payload = {
            "jsonrpc": "2.0",
            "id": "1",
            "method": "message/send",
            "params": {
                "message": {
                    "kind": "message",
                    "message_id": "msg-1",
                    "role": "user",
                    "parts": [{"kind": "text", "text": prompt}]
                }
            }
        }

        try:
            response = requests.post(
                f"{self.server_url}/",
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=60
            )
            response.raise_for_status()
            result = response.json()

            if "error" in result:
                return None

            # A2A 응답에서 데이터 추출
            response_data = result.get("result", {})
            if "history" in response_data:
                for msg in response_data["history"]:
                    if msg.get("role") == "agent" and "parts" in msg:
                        for part in msg["parts"]:
                            if part.get("kind") == "data":
                                data = part.get("data", {})
                                if "response" in data and isinstance(data["response"], dict):
                                    if "ticker" in data["response"]:
                                        return data["response"]

            return None

        except Exception as e:
            print(f"❌ 에러: {e}")
            return None

    def calculate_ticker_score(self, ticker: str):
        """티커 점수 조회"""
        print(f"\n⏳ {ticker} 분석 중...\n")

        result = self._call_a2a(f"Calculate the score for {ticker.upper()}")

        if result:
            self._print_ticker_result(result)
        else:
            print("❌ 결과 없음")

    def get_agent_info(self):
        """에이전트 정보 조회"""
        print("\n⏳ 정보 조회 중...\n")

        result = self._call_a2a("Get agent info")

        if result:
            self._print_agent_info(result)
        else:
            print("❌ 정보 없음")

    def _print_ticker_result(self, result):
        """티커 결과 출력"""
        print("─" * 60)
        print(f"📊 {result.get('ticker')}")
        print("─" * 60)
        print(f"점수: {result.get('score')}/100")
        print(f"근거: {result.get('rationale')}")

        if result.get('price'):
            price = result['price']
            change_symbol = "↑" if price.get('chg', 0) >= 0 else "↓"
            print(f"\n💰 주가: ${price.get('last')} {change_symbol} {price.get('chg')} ({price.get('pct')}%)")

        if result.get('news'):
            print(f"\n📰 뉴스 {len(result['news'])}건:")
            for i, news in enumerate(result['news'][:3], 1):
                title = news.get('title', 'N/A')
                print(f"  {i}. {title[:70]}...")

        print("─" * 60 + "\n")

    def _print_agent_info(self, info):
        """에이전트 정보 출력"""
        print("─" * 60)
        print(f"🤖 {info.get('agent')}")
        print("─" * 60)
        print(info.get('description'))

        print("\n✨ 기능:")
        for cap in info.get('capabilities', []):
            print(f"  • {cap}")

        print(f"\n📊 지원 티커: {', '.join(info.get('example_tickers', []))}")
        print("─" * 60 + "\n")

    def show_help(self):
        """도움말 표시"""
        print("\n" + "─" * 60)
        print("💡 사용 가능한 명령어")
        print("─" * 60)
        print("  <TICKER>     티커 점수 조회 (예: AAPL, MSFT, NVDA)")
        print("  info         에이전트 정보")
        print("  help         이 도움말")
        print("  exit, quit   종료")
        print("─" * 60 + "\n")

    def run(self):
        """대화형 루프 실행"""
        print("🎯 Interactive A2A Client")
        print("명령어를 입력하세요 (도움말: help)\n")

        while True:
            try:
                # 사용자 입력
                command = input("> ").strip()

                if not command:
                    continue

                # 명령어 처리
                command_lower = command.lower()

                if command_lower in ['exit', 'quit', 'q']:
                    print("\n👋 종료합니다.\n")
                    break

                elif command_lower == 'help':
                    self.show_help()

                elif command_lower == 'info':
                    self.get_agent_info()

                else:
                    # 티커로 간주
                    # 여러 티커를 공백으로 구분하여 입력 가능
                    tickers = command.upper().split()

                    if len(tickers) == 1:
                        # 단일 티커
                        self.calculate_ticker_score(tickers[0])
                    else:
                        # 여러 티커 비교
                        print(f"\n📊 {len(tickers)}개 티커 비교 분석\n")
                        results = {}

                        for ticker in tickers:
                            result = self._call_a2a(f"Calculate the score for {ticker}")
                            if result:
                                results[ticker] = result.get('score', 0)
                                print(f"  {ticker:8s} → {result.get('score', 0):3d}/100")

                        if results:
                            avg = sum(results.values()) / len(results)
                            print(f"\n  평균     → {avg:.1f}/100\n")

            except KeyboardInterrupt:
                print("\n\n👋 종료합니다.\n")
                break

            except EOFError:
                print("\n\n👋 종료합니다.\n")
                break

            except Exception as e:
                print(f"\n❌ 에러: {e}\n")


def main():
    """메인 함수"""
    try:
        client = InteractiveClient()
        client.run()
    except Exception:
        sys.exit(1)


if __name__ == "__main__":
    main()
