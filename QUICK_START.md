# Quick Start Guide - Clinic Reservation System

## 🚀 Get Everything Running in 3 Steps

### Step 1: Configure Environment

Create `backend/.env` file:

```env
# Required for AI conversations
GROQ_API_KEY=gsk_your_key_here

# Required for data storage (MCP server)
MCP_SERVER_URL=http://localhost:3001

# Optional - for Google Calendar sync
GOOGLE_SERVICE_ACCOUNT_FILE=service-account.json
GOOGLE_CALENDAR_ID=your_calendar_id@group.calendar.google.com

# Optional - for phone calls and MMS reminders
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_PHONE_NUMBER=+1234567890
```

### Step 2: Start Backend

```bash
cd backend
python main.py
```

**You should see:**
```
✅ Reminder scheduler started
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### Step 3: Start Frontend

```bash
npm run dev
```

**You should see:**
```
VITE ready in XXX ms
➜  Local:   http://localhost:3000/
```

## ✅ Test the Complete Flow

### 1. Open Chat Interface
- Go to: `http://localhost:3000/book`
- You'll see the chat interface

### 2. Start Conversation
Type: **"Hey"** or **"Hello"**

AI responds: *"Hello! I'm here to help you. How can I assist you today?"*

### 3. Book Appointment
Follow this conversation:

**You:** "I want to book an appointment"

**AI:** "I'd be happy to help you book an appointment! Could you please tell me your full name?"

**You:** "My name is Ahmed Boudiaf"

**AI:** "Thank you, Ahmed Boudiaf! Now, could you please provide your phone number?"

**You:** "5551234567"

**AI:** "Great! What date and time would you prefer for your appointment?"

**You:** "Tomorrow at 2 PM"

**AI:** "Let me check the availability... Perfect! I have [date] at 2:00 PM available. Would you like to confirm this appointment?"

**You:** "Yes"

**AI:** "Excellent! Your appointment has been confirmed..."

### 4. Verify Appointment
- Go to: `http://localhost:3000/appointments`
- Search by name: "Ahmed Boudiaf"
- See your appointment listed!

## 🎯 What Happens Behind the Scenes

1. **AI Conversation** → Groq/LLaMA processes your messages
2. **Information Extraction** → AI extracts name, phone, date/time
3. **Availability Check** → Checks Google Calendar + MCP database
4. **Booking** → Creates event in Google Calendar + stores in MCP
5. **Reminder** → Scheduler sends MMS 24 hours before (if Twilio configured)

## 🔍 Verify Everything Works

### Check Backend Logs
When you book, you should see:
```
✅ Appointment booked: Ahmed Boudiaf - 2025-01-15 at 14:00
```

### Check Appointments API
```bash
curl http://localhost:8000/api/appointments/
```

### Check Reminder Scheduler
Look for in backend logs:
```
✅ Reminder scheduler started
```

## ⚠️ Common Issues

**AI not responding:**
- Check `GROQ_API_KEY` in `.env`
- Check backend logs for errors

**Appointments not saving:**
- Check MCP server is running
- Check `MCP_SERVER_URL` in `.env`

**Reminders not sending:**
- Check Twilio credentials in `.env`
- Reminders send 24 hours before appointment

## 📞 Phone Call Support (Optional)

If Twilio is configured:
1. Set webhook in Twilio dashboard: `http://your-domain.com/api/phone/incoming`
2. Call your Twilio number
3. AI answers and guides you through booking

## 🎉 You're All Set!

The system is now running and ready to handle appointments!

For detailed information, see `COMPLETE_SYSTEM_GUIDE.md`



