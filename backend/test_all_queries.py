import sys
import os
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from agents.orchestrator import create_agent_executor

def main():
    load_dotenv()
    
    # We will run this sequence of user queries as requested
    queries = [
        "Read my latest unread emails.",
        "Summarize the unread emails you just read.",
        "Send an email to archijain2112@gmail.com summarizing the previous emails.",
        "Schedule a meeting for tomorrow at 10 AM with you and me to discuss the app.",
        "Set a task on my calendar for tomorrow at 2 PM to review the project status."
    ]
    
    executor = create_agent_executor("end_to_end_test_session")
    
    print("====================================")
    print("STARTING END-TO-END QUERY TESTS")
    print("====================================")
    
    for i, q in enumerate(queries):
        print(f"\n--- [Query {i+1}/{len(queries)}] ---")
        print(f"USER: {q}")
        try:
            res = executor.invoke({"input": q})
            print(f"AGENT: {res.get('output')}")
        except Exception as e:
            import traceback
            print(f"FAILED on query '{q}' WITH EXCEPTION!")
            traceback.print_exc()
            break
            
if __name__ == "__main__":
    main()
