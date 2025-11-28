"""
Phone call API router for voice interactions via Twilio
"""
from fastapi import APIRouter, Request, Form
from twilio.twiml.voice_response import VoiceResponse, Gather
from twilio.request_validator import RequestValidator
from typing import Optional
import os

from app.services.ai_agent import AIAgent
from app.config import settings

router = APIRouter()
ai_agent = AIAgent()

@router.post("/incoming")
async def handle_incoming_call(request: Request):
    """Handle incoming phone call"""
    # Get caller's phone number
    caller = request.form.get("From", "")
    
    # Create TwiML response
    response = VoiceResponse()
    
    # Greeting
    response.say(
        "Hello! Welcome to MediCare Clinic. I'm your AI booking assistant. "
        "I'll help you schedule an appointment. Let me start by getting your information.",
        voice="alice"
    )
    
    # Gather user input
    gather = Gather(
        input="speech",
        action="/api/phone/process",
        method="POST",
        speech_timeout="auto",
        language="en-US"
    )
    gather.say(
        "Please tell me your full name.",
        voice="alice"
    )
    response.append(gather)
    
    # Fallback if no input
    response.say(
        "I didn't receive your name. Please call back and try again.",
        voice="alice"
    )
    response.hangup()
    
    return str(response)

@router.post("/process")
async def process_voice_input(request: Request):
    """Process voice input from phone call"""
    # Get speech result
    speech_result = request.form.get("SpeechResult", "")
    caller = request.form.get("From", "")
    call_sid = request.form.get("CallSid", "")
    
    # Process through AI agent
    session_id = f"phone_{call_sid}"
    response_data = await ai_agent.process_message(
        user_message=speech_result,
        session_id=session_id
    )
    
    # Create TwiML response
    response = VoiceResponse()
    
    # Check if appointment was booked
    if response_data.get("appointment_data"):
        response.say(
            response_data["message"],
            voice="alice"
        )
        response.say(
            "Thank you for using MediCare Clinic. Have a great day!",
            voice="alice"
        )
        response.hangup()
    else:
        # Continue conversation
        gather = Gather(
            input="speech",
            action="/api/phone/process",
            method="POST",
            speech_timeout="auto",
            language="en-US"
        )
        gather.say(
            response_data["message"],
            voice="alice"
        )
        response.append(gather)
        
        # Fallback
        response.say(
            "I didn't catch that. Please try again.",
            voice="alice"
        )
        response.redirect("/api/phone/process")
    
    return str(response)

@router.post("/webhook")
async def twilio_webhook(request: Request):
    """Handle Twilio webhook events"""
    # Validate request (in production, use proper validation)
    data = await request.form()
    
    # Handle different webhook events
    event_type = data.get("EventType", "")
    
    if event_type == "call-status":
        # Handle call status updates
        call_sid = data.get("CallSid", "")
        call_status = data.get("CallStatus", "")
        print(f"Call {call_sid} status: {call_status}")
    
    return {"status": "ok"}





