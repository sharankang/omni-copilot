import traceback

try:
    from langchain.agents import create_tool_calling_agent, AgentExecutor
    print("SUCCESS")
except Exception as e:
    with open("error_trace.txt", "w") as f:
        f.write(traceback.format_exc())
