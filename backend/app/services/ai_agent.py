"""
AI Agent service using Groq (LLaMA) and MCP for natural conversation.
"""
import asyncio
from typing import Dict, Optional, List
import uuid
from datetime import datetime, timedelta
import re

from dateutil import parser as date_parser
from groq import Groq

from app.config import settings
from app.services.calendar import CalendarService
from app.services.mcp_client import MCPClient


class AIAgent:
    """AI Agent for handling patient conversations."""

    def __init__(self):
        if settings.GROQ_API_KEY:
            try:
                self.groq_client = Groq(api_key=settings.GROQ_API_KEY)
                print("✅ Groq client initialized successfully")
            except Exception as e:
                print(f"❌ Failed to initialize Groq client: {e}")
                self.groq_client = None
        else:
            print("⚠️ GROQ_API_KEY not set. AI responses will be limited.")
            self.groq_client = None
        
        # Use model from config (default: llama-3.3-70b-versatile)
        # Can be overridden with GROQ_MODEL in .env
        # Available models: llama-3.3-70b-versatile, llama-3.1-8b-instant, mixtral-8x7b-32768
        self.groq_model = settings.GROQ_MODEL
        self.temperature = 0.7
        print(f"🤖 Using Groq model: {self.groq_model}")

        self.mcp_client = MCPClient()
        self.calendar_service = CalendarService()
        self.sessions: Dict[str, Dict] = {}

        # Load doctors list for system prompt
        from app.routers.doctors import DOCTORS_DATA
        doctors_list = "\n".join([
            f"- {doc['name']} ({doc['specialty']}) - {doc['qualifications']}"
            for doc in DOCTORS_DATA
        ])

        # System prompt for the AI agent
        self.system_prompt = f"""You are a friendly and professional booking assistant for {settings.CLINIC_NAME}. 
Your role is to help patients with any questions or requests through natural conversation.

IMPORTANT - Available Doctors at our clinic:
{doctors_list}

When patients ask about doctors or specialties, ALWAYS refer to the doctors listed above. Never make up doctor names. If they ask for a specific specialty, suggest the appropriate doctor from the list above.

Guidelines:
1. Be warm, empathetic, and professional - respond naturally to ANY message the user sends
2. If the user greets you (hi, hello, hey, etc.), greet them back warmly and ask how you can help
3. If they want to book an appointment, collect the following information in a conversational way:
   - Patient's full name
   - Phone number
   - Preferred appointment date and time
4. Check availability before confirming appointments
5. If the requested time is not available, suggest alternative times (same day first, then nearby days)
6. Use natural language and ask follow-up questions when needed
7. Confirm all details before booking
8. Be patient and understanding
9. Answer questions about the clinic, services, doctors, or anything else related to healthcare
10. If you don't understand something, ask for clarification politely
11. When mentioning doctors, ALWAYS use the exact names from the list above (e.g., "د. أحمد بومدين" for Cardiology, "د. فاطمة الزهراء" for Pediatrics)

Clinic hours: {settings.CLINIC_HOURS_START} to {settings.CLINIC_HOURS_END}
Appointment duration: {settings.APPOINTMENT_DURATION_MINUTES} minutes

Always be helpful, conversational, and make the experience smooth for the patient. Respond naturally to whatever they say."""

    def get_current_time(self) -> datetime:
        """Get current time"""
        return datetime.now()

    def _extract_name(self, message: str) -> Optional[str]:
        """Extract name from message"""
        # Simple pattern matching - can be enhanced with NLP
        patterns = [
            r"my name is ([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)",
            r"i'm ([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)",
            r"i am ([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)",
            r"name is ([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)",
            r"([A-Z][a-z]+\s+[A-Z][a-z]+)",  # Two capitalized words
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None

    def _extract_phone(self, message: str) -> Optional[str]:
        """Extract phone number from message"""
        # Remove common characters and find digits
        digits = re.sub(r'[^\d]', '', message)
        if len(digits) >= 10:
            return digits
        return None

    def _extract_datetime(self, message: str) -> Optional[Dict]:
        """Extract date and time from message"""
        # This is a simplified version - in production, use a proper NLP library
        message_lower = message.lower()
        
        # Check for relative dates
        today = datetime.now()
        date = None
        time = None
        
        # Date patterns
        if "tomorrow" in message_lower:
            date = today + timedelta(days=1)
        elif "today" in message_lower:
            date = today
        elif "monday" in message_lower or "mon" in message_lower:
            days_ahead = (0 - today.weekday()) % 7
            if days_ahead == 0:
                days_ahead = 7
            date = today + timedelta(days=days_ahead)
        elif "tuesday" in message_lower or "tue" in message_lower:
            days_ahead = (1 - today.weekday()) % 7
            if days_ahead == 0:
                days_ahead = 7
            date = today + timedelta(days=days_ahead)
        elif "wednesday" in message_lower or "wed" in message_lower:
            days_ahead = (2 - today.weekday()) % 7
            if days_ahead == 0:
                days_ahead = 7
            date = today + timedelta(days=days_ahead)
        elif "thursday" in message_lower or "thu" in message_lower:
            days_ahead = (3 - today.weekday()) % 7
            if days_ahead == 0:
                days_ahead = 7
            date = today + timedelta(days=days_ahead)
        elif "friday" in message_lower or "fri" in message_lower:
            days_ahead = (4 - today.weekday()) % 7
            if days_ahead == 0:
                days_ahead = 7
            date = today + timedelta(days=days_ahead)
        
        # Time patterns
        time_patterns = [
            r'(\d{1,2})\s*(?:am|pm)',
            r'(\d{1,2}):(\d{2})\s*(?:am|pm)?',
            r'at\s+(\d{1,2})',
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, message_lower)
            if match:
                hour = int(match.group(1))
                minute = int(match.group(2)) if len(match.groups()) > 1 and match.group(2) else 0
                
                if "pm" in message_lower and hour != 12:
                    hour += 12
                elif "am" in message_lower and hour == 12:
                    hour = 0
                
                time = f"{hour:02d}:{minute:02d}"
                break
        
        if date:
            return {"date": date, "time": time}
        return None

    async def process_message(self, user_message: str, session_id: str = None) -> Dict:
        """Process user message and generate AI response"""
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # Initialize or get session
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "state": "collecting_name",
                "patient_name": None,
                "patient_phone": None,
                "requested_date": None,
                "requested_time": None,
                "conversation_history": []
            }
        
        session = self.sessions[session_id]
        session["conversation_history"].append({"role": "user", "content": user_message})
        
        print(f"\n📨 Processing message: '{user_message[:50]}...'")
        print(f"   Session state: {session['state']}")
        print(f"   Groq client available: {self.groq_client is not None}")
        
        # Extract information in the background (for booking flow)
        state_based_response = None
        booking_action = None
        
        if session["state"] == "collecting_name":
            name = self._extract_name(user_message)
            if name:
                session["patient_name"] = name
                session["state"] = "collecting_phone"
                # Don't override LLM response, just update state
        
        elif session["state"] == "collecting_phone":
            phone = self._extract_phone(user_message)
            if phone:
                session["patient_phone"] = phone
                session["state"] = "collecting_datetime"
                # Don't override LLM response, just update state
        
        elif session["state"] == "collecting_datetime":
            datetime_info = self._extract_datetime(user_message)
            if datetime_info:
                session["requested_date"] = datetime_info["date"]
                session["requested_time"] = datetime_info["time"]
                session["state"] = "checking_availability"
                
                # Check availability
                is_available = await self.calendar_service.check_availability(
                    session["requested_date"],
                    session["requested_time"]
                )
                
                if is_available:
                    session["state"] = "confirming"
                    # Store availability info for LLM context
                    state_based_response = f"Perfect! I have {session['requested_date'].strftime('%A, %B %d')} at {session['requested_time']} available. Would you like to confirm this appointment?"
                else:
                    # Find alternative times
                    alternatives = await self.calendar_service.find_alternatives(
                        session["requested_date"],
                        session["requested_time"]
                    )

                    if alternatives:
                        alt_texts = []
                        for alt in alternatives[:3]:
                            alt_date = alt.get("date")
                            alt_time = alt.get("time")
                            try:
                                alt_dt = date_parser.isoparse(alt_date) if isinstance(alt_date, str) else alt_date
                                label = alt_dt.strftime("%A at %I:%M %p")
                            except Exception:
                                label = f"{alt_date} at {alt_time}"
                            if alt_time and alt_time not in label:
                                label = f"{label.split(' at ')[0]} at {alt_time}"
                            alt_texts.append(label)

                        alt_text = ", ".join(alt_texts) if alt_texts else None
                        if alt_text:
                            state_based_response = f"I'm sorry, but that time slot is not available. However, I have these alternative times: {alt_text}. Would any of these work for you?"
        
        elif session["state"] == "confirming":
            if any(word in user_message.lower() for word in ["yes", "confirm", "ok", "sure", "that works"]):
                # Book the appointment
                appointment = await self.calendar_service.book_appointment(
                    patient_name=session["patient_name"],
                    patient_phone=session["patient_phone"],
                    appointment_date=session["requested_date"],
                    appointment_time=session["requested_time"]
                )
                
                if appointment:
                    session["state"] = "completed"
                    response = f"Excellent! Your appointment has been confirmed for {session['requested_date'].strftime('%A, %B %d')} at {session['requested_time']}. You'll receive a reminder message before your appointment. Is there anything else I can help you with?"
                    
                    return {
                        "message": response,
                        "session_id": session_id,
                        "appointment_data": {
                            "id": appointment["id"],
                            "date": appointment["appointment_date"] if isinstance(appointment["appointment_date"], str) else appointment["appointment_date"].isoformat(),
                            "time": appointment["appointment_time"]
                        }
                    }
                else:
                    state_based_response = "I apologize, but there was an issue booking your appointment. Please try again or contact us directly."
            elif any(word in user_message.lower() for word in ["no", "cancel", "change"]):
                session["state"] = "collecting_datetime"
        
        # Always try to use LLM for natural responses FIRST
        response = None
        if self.groq_client:
            try:
                llm_response = await self._generate_natural_response(session, user_message)
                if llm_response and llm_response.strip():
                    response = llm_response.strip()
                    print(f"✅ LLM response generated: {response[:50]}...")
                else:
                    print("⚠️ LLM returned empty response")
            except Exception as e:
                print(f"❌ Error generating LLM response: {e}")
                import traceback
                traceback.print_exc()
        
        # If LLM didn't respond, use state-based response if available
        if not response:
            if state_based_response:
                response = state_based_response
                print(f"📝 Using state-based response: {response[:50]}...")
            else:
                # Only use default if we have no other response
                if not self.groq_client:
                    response = "I'm here to help! However, I need a Groq API key to provide intelligent responses. Please configure GROQ_API_KEY in your .env file. How can I assist you with booking an appointment?"
                else:
                    # If LLM failed, provide a more helpful default
                    response = "I'm here to help! How can I assist you today?"
                print(f"⚠️ Using default response (no LLM or state response)")
        
        session["conversation_history"].append({"role": "assistant", "content": response})
        
        return {
            "message": response,
            "session_id": session_id,
            "appointment_data": None
        }

    async def _generate_natural_response(self, session: Dict, user_message: str) -> Optional[str]:
        """Generate a natural-sounding response using Groq / LLaMA."""
        if not self.groq_client:
            return None

        # Add current booking state to system prompt if in booking flow
        system_prompt = self.system_prompt
        if session.get("state") != "collecting_name" and session.get("patient_name"):
            state_info = f"\n\nCurrent booking context: Patient name: {session.get('patient_name')}"
            if session.get("patient_phone"):
                state_info += f", Phone: {session.get('patient_phone')}"
            if session.get("requested_date"):
                state_info += f", Requested date/time: {session.get('requested_date')} at {session.get('requested_time')}"
            system_prompt += state_info

        messages: List[Dict[str, str]] = [
            {"role": "system", "content": system_prompt},
        ]

        # Include conversation history for better context
        # Skip the last message since we're adding it separately
        history = session["conversation_history"][:-1] if session["conversation_history"] else []
        for msg in history[-10:]:  # Last 10 messages for context
            if msg.get("role") and msg.get("content"):
                messages.append({"role": msg["role"], "content": msg["content"]})

        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        print(f"📤 Sending {len(messages)} messages to Groq LLM")

        def _invoke():
            return self.groq_client.chat.completions.create(
                model=self.groq_model,
                temperature=self.temperature,
                messages=messages,
            )

        try:
            completion = await asyncio.to_thread(_invoke)
            if completion and completion.choices:
                content = completion.choices[0].message.content
                if content:
                    return content.strip()
            else:
                print("⚠️ Groq API returned empty completion")
        except Exception as exc:  # pylint: disable=broad-except
            print(f"❌ Error calling Groq LLM: {exc}")
            import traceback
            traceback.print_exc()
        return None

