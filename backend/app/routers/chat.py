"""
Chat API router for text-based interactions
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.services.ai_agent import AIAgent

router = APIRouter()
ai_agent = AIAgent()

class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    message: str
    session_id: str
    appointment_data: Optional[dict] = None

@router.post("/", response_model=ChatResponse)
async def chat(message: ChatMessage):
    """Process a chat message and get AI response"""
    try:
        response = await ai_agent.process_message(
            user_message=message.message,
            session_id=message.session_id
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing message: {str(e)}")

@router.post("/session/new")
async def create_session():
    """Create a new chat session"""
    import uuid
    session_id = str(uuid.uuid4())
    return {"session_id": session_id}





