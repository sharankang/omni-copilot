from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from agents.orchestrator import create_agent_executor, memory_store
import os
import logging
import shutil
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter()

# Setup uploads directory
UPLOADS_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(UPLOADS_DIR, exist_ok=True)

@router.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    try:
        # Generate safe file path
        safe_filename = file.filename.replace(" ", "_")
        file_path = os.path.join(UPLOADS_DIR, f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{safe_filename}")
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        return {"status": "success", "file_path": file_path, "filename": safe_filename}
    except Exception as e:
        logger.error(f"Error uploading file: {e}")
        raise HTTPException(status_code=500, detail=str(e))

class ChatRequest(BaseModel):
    message: str
    session_id: str

# To maintain session titles and creation times globally
session_metadata = {}

@router.post("")
def chat_endpoint(request: ChatRequest):
    try:
        # Register new session metadata if not exists
        if request.session_id not in session_metadata:
            session_metadata[request.session_id] = {
                "id": request.session_id,
                "title": request.message[:35] + ("..." if len(request.message) > 35 else ""),
                "created_at": datetime.utcnow().isoformat() + "Z"
            }
            
        agent_executor = create_agent_executor(request.session_id)
        
        try:
            result = agent_executor.invoke({"input": request.message})
        except Exception as invoke_err:
            logger.warning("Agent invoke failed (%s); falling back to direct LLM.", str(invoke_err))
            try:
                from langchain_groq import ChatGroq
                from langchain_core.messages import HumanMessage
                groq_key = os.getenv("GROQ_API_KEY")
                fallback_llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0, groq_api_key=groq_key)
                fallback_resp = fallback_llm.invoke([HumanMessage(content=request.message)])
                output = getattr(fallback_resp, "content", str(fallback_resp))
            except Exception as fallback_err:
                logger.error("Fallback LLM failed too: %s", str(fallback_err))
                output = f"I'm currently experiencing connectivity issues or rate limits. Please try again later. (Error: {str(fallback_err)})"
            
            # Manually append to memory_store since executor failed
            from agents.orchestrator import get_memory
            mem = get_memory(request.session_id)
            mem.chat_memory.add_user_message(request.message)
            mem.chat_memory.add_ai_message(output)
            
            error_message = f"**[SYSTEM DIAGNOSTIC: AGENT CRASHED]**\n\nThe LLM agent engine crashed internally when trying to initialize tools. \n\n**Raw Error Stack:** `{str(invoke_err)}`\n\n**Fallback LLM Response:**\n{output}"
            
            return {"response": error_message, "session_id": request.session_id}

        output = result.get("output", result.get("response", str(result)))
        return {"response": output, "session_id": request.session_id}
        
    except Exception as e:
        import traceback
        traceback.print_exc()
        # Instead of 500, we should fail gracefully just in case
        return {"response": f"An unexpected error occurred: {str(e)}", "session_id": request.session_id}

@router.get("/sessions")
async def get_sessions():
    """Returns a list of actively maintained chat sessions."""
    res = list(session_metadata.values())
    # Sort by created_at descending
    res.sort(key=lambda x: x["created_at"], reverse=True)
    return {"sessions": res}

@router.get("/{session_id}")
async def get_session(session_id: str):
    """Retrieves all historical messages for a specific session."""
    if session_id not in memory_store:
        return {"messages": []}
        
    msgs = memory_store[session_id].chat_memory.messages
    formatted = []
    for i, m in enumerate(msgs):
        role = "user" if m.type == "human" else "ai"
        formatted.append({"id": f"{session_id}_{i}", "role": role, "content": m.content})
    return {"messages": formatted}

@router.delete("/{session_id}")
async def delete_session(session_id: str):
    """Deletes a session from active memory."""
    if session_id in memory_store:
        del memory_store[session_id]
    if session_id in session_metadata:
        del session_metadata[session_id]
    return {"success": True}
