import sys
import os
sys.path.insert(0, '/Users/archijain/Downloads/omni_copilot/backend')

from agents.orchestrator import create_agent_executor

def test():
    try:
        executor = create_agent_executor("test_session_99")
        print("Executing agent...")
        res = executor.invoke({"input": "Read my latest unread emails."})
        print("\n\nSUCCESS! Result:", res)
    except Exception as e:
        import traceback
        print("\n\nFAILED WITH EXCEPTION!")
        traceback.print_exc()

if __name__ == "__main__":
    test()
