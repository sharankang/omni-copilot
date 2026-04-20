import traceback
from agents.orchestrator import create_agent_executor

def test():
    try:
        executor = create_agent_executor("test_session_calendar")
        print("Executing agent with calendar prompt...")
        res = executor.invoke({"input": "Read my calendar for upcoming events."})
        print("\n\nSUCCESS! Result:", res)
    except Exception as e:
        print("\n\nFAILED WITH EXCEPTION!")
        traceback.print_exc()

if __name__ == "__main__":
    test()
