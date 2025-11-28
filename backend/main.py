"""
Main FastAPI application for Clinic Reservation App
Supports AI agent interactions via chat and phone calls
"""
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import uvicorn
from typing import List
import json
from app.routers import appointments, chat, phone, doctors
from app.services.ai_agent import AIAgent
from app.services.scheduler import ReminderScheduler
from app.config import settings

# Initialize AI Agent and Scheduler
ai_agent = AIAgent()
reminder_scheduler = ReminderScheduler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup resources.

    Note: there is no local database anymore. All persistent data
    lives in the MCP server, so we only need to start/stop the
    reminder scheduler here.
    """
    # Startup
    reminder_scheduler.start()
    print("✅ Reminder scheduler started")
    yield
    # Shutdown
    reminder_scheduler.stop()
    print("✅ Reminder scheduler stopped")

app = FastAPI(
    title="Clinic Reservation API",
    description="AI-powered clinic reservation system with chat and phone support",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(appointments.router, prefix="/api/appointments", tags=["appointments"])
app.include_router(chat.router, prefix="/api/chat", tags=["chat"])
app.include_router(phone.router, prefix="/api/phone", tags=["phone"])
app.include_router(doctors.router, prefix="/api/doctors", tags=["doctors"])

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

@app.get("/")
async def root():
    return {
        "message": "Clinic Reservation API",
        "version": "1.0.0",
        "endpoints": {
            "chat": "/api/chat",
            "phone": "/api/phone",
            "appointments": "/api/appointments",
            "websocket": "/ws"
        }
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "clinic-reservation-api"}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time chat"""
    await manager.connect(websocket)
    try:
        # Send welcome message
        welcome_msg = {
            "type": "assistant",
            "message": "Hello! I'm here to help you book an appointment at MediCare Clinic. Could you please provide your full name?",
            "timestamp": str(ai_agent.get_current_time())
        }
        await websocket.send_text(json.dumps(welcome_msg))
        
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            # Process message through AI agent
            response = await ai_agent.process_message(
                user_message=message_data.get("message", ""),
                session_id=message_data.get("session_id", "default")
            )
            
            # Send response back
            response_msg = {
                "type": "assistant",
                "message": response["message"],
                "session_id": response.get("session_id"),
                "appointment_data": response.get("appointment_data"),
                "timestamp": str(ai_agent.get_current_time())
            }
            await websocket.send_text(json.dumps(response_msg))
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )

