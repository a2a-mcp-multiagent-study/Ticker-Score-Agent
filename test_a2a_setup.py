#!/usr/bin/env python
"""
A2A Setup 테스트 스크립트
google-adk 설치 여부 확인 및 import 테스트
"""
import sys

def test_imports():
    """필요한 모듈 import 테스트"""
    print("=" * 60)
    print("A2A Setup Test")
    print("=" * 60)

    # 1. google-adk 체크
    print("\n[1/4] Checking google-adk installation...")
    try:
        import google.adk
        print("✓ google-adk is installed")
        print(f"  Version: {getattr(google.adk, '__version__', 'unknown')}")
    except ImportError as e:
        print("✗ google-adk is NOT installed")
        print(f"  Error: {e}")
        print("\n  Install with: pip install google-adk")
        return False

    # 2. A2A Agent 모듈 체크
    print("\n[2/4] Checking app.workflow.a2a_agent...")
    try:
        from app.workflow.a2a_agent import ticker_agent, calculate_ticker_score
        print("✓ a2a_agent module loaded successfully")
        print(f"  Agent name: {ticker_agent.name}")
        print(f"  Agent description: {ticker_agent.description}")
        print(f"  Tools: {len(ticker_agent.tools)} available")
    except ImportError as e:
        print(f"✗ Failed to import a2a_agent: {e}")
        return False
    except Exception as e:
        print(f"✗ Error loading a2a_agent: {e}")
        return False

    # 3. A2A Server 모듈 체크
    print("\n[3/4] Checking app.a2a_server...")
    try:
        from app.a2a_server import a2a_app
        print("✓ a2a_server module loaded successfully")
        print(f"  FastAPI app type: {type(a2a_app).__name__}")
    except ImportError as e:
        print(f"✗ Failed to import a2a_server: {e}")
        return False
    except Exception as e:
        print(f"✗ Error loading a2a_server: {e}")
        return False

    # 4. 기존 워크플로우 체크
    print("\n[4/4] Checking existing workflow...")
    try:
        from app.workflow.graph import run_once, graph
        print("✓ LangGraph workflow is accessible")
        print(f"  Graph nodes: {list(graph.nodes.keys())}")
    except ImportError as e:
        print(f"✗ Failed to import workflow: {e}")
        return False
    except Exception as e:
        print(f"✗ Error loading workflow: {e}")
        return False

    print("\n" + "=" * 60)
    print("✓ All checks passed!")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Start A2A server:")
    print("     uvicorn app.a2a_server:a2a_app --port 8083 --reload")
    print("\n  2. Check agent card:")
    print("     curl http://localhost:8083/.well-known/agent-card.json")
    print("\n  3. Test with host agent:")
    print("     python -m a2a-poc.host.agent_with_ticker")
    print("=" * 60)

    return True


if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
