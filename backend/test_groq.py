import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage

load_dotenv()
groq_key = os.getenv("GROQ_API_KEY")
print("Key starts with:", groq_key[:10] if groq_key else None)

try:
    llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0, groq_api_key=groq_key)
    resp = llm.invoke([HumanMessage(content="Hello")])
    print("Success:", resp.content)
except Exception as e:
    print("Failed")
    import traceback
    traceback.print_exc()
