'''
AI Agent service using Groq (LLaMA) and MCP for natural conversation.
'''
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
    '''AI Agent for handling patient conversations.'''

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
        self.doctors_data = DOCTORS_DATA
        doctors_list = "\n".join([
            f"- {doc['name']} ({doc['specialty']}) - {doc['qualifications']}"
            for doc in self.doctors_data
        ])

        # System prompt for the AI agent
        self.system_prompt = f'''You are a friendly and professional booking assistant for {settings.CLINIC_NAME}. 
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

Always be helpful, conversational, and make the experience smooth for the patient. Respond naturally to whatever they say.'''

    def get_current_time(self) -> datetime:
        '''Get current time'''
        return datetime.now()

    def _extract_name(self, message: str) -> Optional[str]:
        '''Extract name from message'''
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
        '''Extract phone number from message'''
        # Remove common characters and find digits
        digits = re.sub(r'[^\d]', '', message)
        if len(digits) >= 10:
            return digits
        return None

    def _extract_datetime(self, message: str) -> Optional[Dict]:
        '''Extract date and time from message'''
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

    def _extract_doctor(self, message: str) -> Optional[Dict]:
        '''Extract doctor name or specialty from message and return doctor data.'''
        message_lower = message.lower()
        
        for doctor in self.doctors_data:
            # Check for doctor name (case-insensitive, partial match for Arabic names)
            if doctor["name"].lower() in message_lower:
                return doctor
            # Check for specialty
            if doctor["specialty"].lower() in message_lower:
                return doctor
        
        return None

    async def process_message(self, user_message: str, session_id: str = None) -> Dict:
        '''Process user message and generate AI response'''
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # Initialize or get session
        if session_id not in self.sessions:
            self.sessions[session_id] = {
                "state": "collecting_doctor", # Start by collecting doctor/specialty
                "patient_name": None,
                "patient_phone": None,
                "requested_date": None,
                "requested_time": None,
                "requested_doctor_id": None,
                "requested_doctor_name": None,
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
        
        if session["state"] == "collecting_doctor":
            doctor = self._extract_doctor(user_message)
            if doctor:
                session["requested_doctor_id"] = doctor["id"]
                session["requested_doctor_name"] = doctor["name"]
                session["state"] = "collecting_name"
                # Don't override LLM response, just update state
        
        elif session["state"] == "collecting_name":
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
                    session["requested_time"],
                    session["requested_doctor_id"]
                )
                
                if is_available:
                    session["state"] = "confirming"
                    # Store availability info for LLM context
                    state_based_response = f"Perfect! I have {session['requested_date'].strftime('%A, %B %d')} at {session['requested_time']} available with {session['requested_doctor_name']}. Would you like to confirm this appointment?"
                else:
                    # Find alternative times
                    alternatives = await self.calendar_service.find_alternatives(
                        session["requested_date"],
                        session["requested_time"],
                        session["requested_doctor_id"]
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
                            state_based_response = f"I'm sorry, but that time slot is not available with {session['requested_doctor_name']}. However, I have these alternative times: {alt_text}. Would any of these work for you?"
        
        elif session["state"] == "confirming":
            if any(word in user_message.lower() for word in ["yes", "confirm", "ok", "sure", "that works"]):
                # Book the appointment
                appointment = await self.calendar_service.book_appointment(
                    patient_name=session["patient_name"],
                    patient_phone=session["patient_phone"],
                    appointment_date=session["requested_date"],
                    appointment_time=session["requested_time"],
                    doctor_id=session["requested_doctor_id"],
                    doctor_name=session["requested_doctor_name"]
                )
                
                if appointment:
                    session["state"] = "completed"
                    booking_action = "booked"
                    state_based_response = f"Excellent! Your appointment with {session['requested_doctor_name']} is confirmed for {session['requested_date'].strftime('%A, %B %d')} at {session['requested_time']}. You'll receive a confirmation message shortly. Is there anything else I can help you with?"
                else:
                    session["state"] = "failed"
                    state_based_response = "I'm sorry, there was an error booking your appointment. Please try again later."
            else:
                session["state"] = "collecting_datetime" # Go back to collecting new time
                state_based_response = "No problem. What other time would you like to book?"

        # Use Groq for conversational responses
        ai_response = await self._get_groq_response(session, state_based_response)

        # Append AI response to history
        session["conversation_history"].append({
            "role": "assistant",
            "content": ai_response
        })

        return {
            "response": ai_response,
            "session_id": session_id,
            "state": session["state"],
            "booking_action": booking_action
        }

    async def _get_groq_response(self, session: Dict, state_based_response: Optional[str]) -> str:
        '''Get response from Groq LLM'''
        if not self.groq_client:
            return state_based_response or "I'm sorry, the AI service is currently unavailable. Please try again later."

        # Create a message list for the LLM
        messages = [
            {"role": "system", "content": self.system_prompt},
            *session["conversation_history"]
        ]

        # Add state-based response as a system message to guide the LLM
        if state_based_response:
            messages.append({
                "role": "system",
                "content": f"IMPORTANT: Use the following information to respond to the user: {state_based_response}"
            })

        try:
            chat_completion = self.groq_client.chat.completions.create(
                messages=messages,
                model=self.groq_model,
                temperature=self.temperature,
                max_tokens=1024,
                top_p=1,
                stop=None,
                stream=False,
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            print(f"❌ Groq API error: {e}")
            return state_based_response or "I'm sorry, I encountered an error. Please try again."
