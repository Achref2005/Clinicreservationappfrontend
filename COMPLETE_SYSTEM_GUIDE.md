# Complete Clinic Reservation System Guide

This guide explains how the entire system works end-to-end, from patient interaction to appointment booking and reminders.

## 🎯 System Overview

The clinic reservation app allows patients to:
1. **Chat with AI** (via web interface)
2. **Call the clinic** (via phone - Twilio)
3. **Book appointments** through natural conversation
4. **Receive reminders** via MMS before appointments

## 🔄 Complete Flow

### Step 1: Patient Initiates Conversation

**Via Chat (Web):**
- Patient visits the website and opens the chat interface
- AI greets: "Hello! I'm here to help you. How can I assist you today?"
- Patient can say anything: "Hey", "I want to book", "Hello", etc.
- AI responds naturally and guides the conversation

**Via Phone Call:**
- Patient calls the Twilio phone number
- AI answers: "Hello! Welcome to MediCare Clinic. I'm your AI booking assistant..."
- Patient speaks naturally, AI processes speech

### Step 2: AI Collects Information

The AI agent collects three pieces of information through natural conversation:

1. **Full Name**
   - AI asks: "Could you please tell me your full name?"
   - Patient responds: "My name is Ahmed Boudiaf" or "I'm Fatima Zohra"
   - AI extracts and confirms the name

2. **Phone Number**
   - AI asks: "Thank you! Now, could you please provide your phone number?"
   - Patient responds: "5551234567" or "+2135551234567"
   - AI extracts the phone number

3. **Date and Time**
   - AI asks: "What date and time would you prefer for your appointment?"
   - Patient responds: "Tomorrow at 2 PM" or "Next Monday at 10 AM"
   - AI extracts date and time

### Step 3: Availability Check

When the patient provides a date/time:

1. **AI checks availability:**
   - Checks Google Calendar (if configured)
   - Checks MCP database for conflicts
   - Verifies time is within clinic hours (9 AM - 5 PM)

2. **If time slot is AVAILABLE:**
   - AI confirms: "Perfect! I have [date] at [time] available. Would you like to confirm this appointment?"
   - Patient says "Yes" → Proceeds to booking

3. **If time slot is NOT AVAILABLE:**
   - AI suggests alternatives: "I'm sorry, but that time slot is not available. However, I have these alternative times: [options]. Would any of these work for you?"
   - AI prioritizes same day first, then nearby days
   - Patient can choose an alternative or request a different time

### Step 4: Appointment Booking

When patient confirms:

1. **AI books the appointment:**
   - Creates event in Google Calendar (if configured)
   - Stores metadata in MCP database
   - Returns confirmation with appointment ID

2. **AI confirms:**
   - "Excellent! Your appointment has been confirmed for [date] at [time]. You'll receive a reminder message before your appointment. Is there anything else I can help you with?"

### Step 5: Automated Reminder

**24 hours before appointment:**

1. **Scheduler runs every hour:**
   - Checks for appointments that need reminders
   - Finds appointments 24 hours away

2. **Sends MMS reminder:**
   - Uses Twilio to send SMS/MMS to patient's phone
   - Message includes: date, time, clinic name
   - Marks reminder as sent in MCP database

## 🛠️ Technical Components

### 1. AI Agent (`ai_agent.py`)
- **Purpose:** Natural language conversation with patients
- **Features:**
  - Conversational responses (uses Groq/LLaMA)
  - Information extraction (name, phone, date/time)
  - State management for booking flow
  - Availability checking integration

### 2. Calendar Service (`calendar.py`)
- **Purpose:** Manage appointments
- **Features:**
  - Check availability (Google Calendar + MCP)
  - Find alternative time slots
  - Book appointments (Google Calendar + MCP)
  - Cancel appointments

### 3. MCP Client (`mcp_client.py`)
- **Purpose:** Store and retrieve appointment metadata
- **Features:**
  - Store appointment data
  - Query appointments by date/phone
  - Mark reminders as sent
  - All persistent data lives here

### 4. Google Calendar Service (`google_calendar.py`)
- **Purpose:** Sync with Google Calendar
- **Features:**
  - Create calendar events
  - Check for conflicts
  - Delete events (on cancellation)
  - Optional but recommended

### 5. MMS Service (`mms_service.py`)
- **Purpose:** Send appointment reminders
- **Features:**
  - Send SMS/MMS via Twilio
  - Format reminder messages
  - Handle errors gracefully

### 6. Reminder Scheduler (`scheduler.py`)
- **Purpose:** Automated reminder system
- **Features:**
  - Runs every hour
  - Checks for appointments needing reminders
  - Sends MMS reminders
  - Marks reminders as sent

### 7. Phone Router (`phone.py`)
- **Purpose:** Handle phone calls via Twilio
- **Features:**
  - Answer incoming calls
  - Process speech input
  - Integrate with AI agent
  - Return TwiML responses

## 📋 Configuration Requirements

### Required (for basic functionality):
- ✅ **Groq API Key** - For AI conversations
- ✅ **MCP Server** - For data storage (default: http://localhost:3001)

### Optional (for full functionality):
- ⚙️ **Google Calendar** - For calendar sync
  - `GOOGLE_SERVICE_ACCOUNT_FILE` - Path to service account JSON
  - `GOOGLE_CALENDAR_ID` - Calendar ID
- ⚙️ **Twilio** - For phone calls and MMS
  - `TWILIO_ACCOUNT_SID`
  - `TWILIO_AUTH_TOKEN`
  - `TWILIO_PHONE_NUMBER`

## 🚀 Running the System

### 1. Start Backend

```bash
cd backend
python main.py
```

**What happens:**
- FastAPI server starts on port 8000
- Reminder scheduler starts (runs every hour)
- AI agent initializes
- Calendar service connects to Google Calendar (if configured)
- MMS service initializes (if Twilio configured)

**Expected output:**
```
✅ Reminder scheduler started
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 2. Start Frontend

```bash
npm run dev
```

**What happens:**
- React app starts (usually port 3000 or 5173)
- Connects to backend API
- Chat interface ready

### 3. Test the Flow

**Test Chat Booking:**
1. Open `http://localhost:3000/book`
2. Type: "Hey" → AI responds naturally
3. Type: "I want to book an appointment"
4. Follow the conversation:
   - Provide name: "My name is Ahmed"
   - Provide phone: "5551234567"
   - Provide time: "Tomorrow at 2 PM"
5. Confirm: "Yes"
6. ✅ Appointment booked!

**Test Phone Call (if Twilio configured):**
1. Call your Twilio number
2. AI answers and guides you through booking
3. Speak naturally
4. ✅ Appointment booked!

**Verify Appointment:**
1. Visit `http://localhost:3000/appointments`
2. Search by name or phone
3. See your appointment listed

**Check Reminders:**
- Reminders are sent automatically 24 hours before
- Check backend logs for: "✅ Reminder sent to [name]"
- Patient receives SMS/MMS on their phone

## 🔍 How to Verify Everything Works

### 1. Check Backend Logs

When booking an appointment, you should see:
```
✅ Appointment booked: Ahmed Boudiaf - 2025-01-15 at 14:00
```

### 2. Check MCP Database

Run verification script:
```bash
cd backend
python verify_booking.py
```

### 3. Check Google Calendar

If configured, open your Google Calendar and see the event.

### 4. Test Reminder System

To test immediately (without waiting 24 hours):

1. Book an appointment for 1 hour from now
2. Wait for the next hour (scheduler runs at :00)
3. Check backend logs for reminder sent
4. Check patient's phone for SMS/MMS

Or modify `REMINDER_HOURS_BEFORE` in `.env` to a smaller value for testing.

## 📝 Example Conversation Flow

**Patient:** "Hey"
**AI:** "Hello! I'm here to help you. How can I assist you today?"

**Patient:** "I want to book an appointment"
**AI:** "I'd be happy to help you book an appointment! Could you please tell me your full name?"

**Patient:** "My name is Ahmed Boudiaf"
**AI:** "Thank you, Ahmed Boudiaf! Now, could you please provide your phone number?"

**Patient:** "5551234567"
**AI:** "Great! What date and time would you prefer for your appointment? For example, you can say 'Tomorrow at 2 PM' or 'Next Monday at 10 AM'."

**Patient:** "Tomorrow at 2 PM"
**AI:** "Let me check the availability... Perfect! I have tomorrow at 2:00 PM available. Would you like to confirm this appointment?"

**Patient:** "Yes"
**AI:** "Excellent! Your appointment has been confirmed for tomorrow at 2:00 PM. You'll receive a reminder message before your appointment. Is there anything else I can help you with?"

## 🎯 Key Features

✅ **Natural Conversation** - AI responds to any message naturally
✅ **Information Extraction** - Automatically extracts name, phone, date/time
✅ **Availability Checking** - Checks both Google Calendar and MCP
✅ **Alternative Suggestions** - Suggests same day or nearby times
✅ **Calendar Integration** - Stores in Google Calendar (if configured)
✅ **MCP Storage** - All metadata stored in MCP database
✅ **Automated Reminders** - Sends MMS 24 hours before
✅ **Phone Support** - Voice calls via Twilio (if configured)
✅ **Error Handling** - Graceful handling of all errors

## 🐛 Troubleshooting

**AI not responding naturally:**
- Check `GROQ_API_KEY` is set in `.env`
- Check backend logs for Groq API errors

**Appointments not saving:**
- Check MCP server is running at `MCP_SERVER_URL`
- Check backend logs for MCP connection errors

**Reminders not sending:**
- Check Twilio credentials in `.env`
- Check scheduler is running (should see "✅ Reminder scheduler started")
- Check backend logs for reminder errors

**Phone calls not working:**
- Check Twilio credentials
- Configure webhook URL in Twilio dashboard
- Check backend logs for phone call errors

## 📚 Next Steps

1. ✅ Configure Google Calendar (optional but recommended)
2. ✅ Configure Twilio for phone/MMS (optional)
3. ✅ Set up MCP server (required for data storage)
4. ✅ Test complete flow end-to-end
5. ✅ Deploy to production

---

**The system is fully functional and ready to use!** 🎉



