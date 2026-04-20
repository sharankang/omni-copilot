from langchain_groq import ChatGroq
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferWindowMemory
from tools.all_tools import OMNI_TOOLS
from typing import Dict
import os
import logging

# Store memory instances per session (rudimentary in-memory storage)
memory_store: Dict[str, ConversationBufferWindowMemory] = {}

def get_memory(session_id: str) -> ConversationBufferWindowMemory:
    if session_id not in memory_store:
        memory_store[session_id] = ConversationBufferWindowMemory(
            memory_key="chat_history", 
            return_messages=True,
            k=3
        )
    return memory_store[session_id]

def create_agent_executor(session_id: str) -> AgentExecutor:
    """Creates and returns an AgentExecutor bound to our tools and memory."""
    from datetime import datetime
    current_time = datetime.now().astimezone().isoformat()
    
    from dotenv import load_dotenv
    load_dotenv()

    # API key is automatically loaded from environment variable GROQ_API_KEY
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise RuntimeError("GROQ_API_KEY is missing from environment. Set it in your .env file.")
    logger = logging.getLogger("omni_copilot.orchestrator")
    logger.debug("GROQ_API_KEY loaded (len=%d)", len(groq_api_key))

    # Bypass 70B Rate Limit by routing to 8b-instant
    llm = ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0,
        groq_api_key=groq_api_key,
        max_tokens=512,
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", f"You are Omni Copilot, an AI-powered unified workspace assistant. "
                   f"The user's name is Sharanpreet Kaur. When drafting the 'message' or 'body' argument for any tool, append her name as a signature. "
                   f"CRITICAL RULE: When asked to perform an action (send an email, slack message, etc), you MUST invoke the actual tool provided to you physically! NEVER simply type 'I have sent the message' in plain text. You MUST execute the tool. After the tool returns success, THEN write a friendly conversational summary to the user.\n"
                   f"The current date and local time is {current_time}. "
                   "CRITICAL TIMEZONE RULE: When providing 'start_time' and 'end_time' for meetings, ALWAYS use strict ISO 8601 format INCLUDING the local timezone offset shown in the current time string (e.g., 2026-04-16T16:00:00+05:30). NEVER use 'Z' (UTC) unless mathematically offset.\n\n"
                   "You can help the user schedule meetings, send emails, read files, send messages to slack/discord, and fetch github files. "
                   "CRITICAL INSTRUCTION: When scheduling a meeting, NEVER use the send_email_tool afterward! Google Calendar natively sends a highly professional, interactive Calendar Invite to attendees automatically. Instead, just use schedule_meeting_tool, ALWAYS draft a high-quality 'description' parameter explaining the agenda professionally, and then simply tell the user you dispatched the professional native calendar invite natively!\n\n"
                   "CRITICAL TOOL INSTRUCTION: NEVER output raw XML or `<function>` tags when calling tools! Always use the native silent JSON tool calling formatting handled by the API."),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    # Standard tool calling agent
    agent = create_tool_calling_agent(llm, OMNI_TOOLS, prompt)

    memory = get_memory(session_id)

    # Combine into executor with loop & parse error prevention to speed up execution
    agent_executor = AgentExecutor(
        agent=agent,
        tools=OMNI_TOOLS,
        memory=memory,
        verbose=True,
        max_iterations=8,
        handle_parsing_errors=True,
        early_stopping_method="force",
    )
    logger.debug("AgentExecutor created for session='%s'", session_id)
    return agent_executor
