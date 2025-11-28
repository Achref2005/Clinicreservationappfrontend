# Clinic Reservation App - Backend

Python backend for the Clinic Reservation App with AI agent, MCP support, automation, and MMS capabilities.

## Features

- 🤖 **AI Agent**: Natural language conversation for booking appointments
- 📞 **Phone Support**: Voice interactions via Twilio
- 💬 **WebSocket Chat**: Real-time chat interface
- 📅 **Calendar Management**: Appointment scheduling with availability checking
- 📱 **MMS Reminders**: Automated appointment reminders via MMS
- ⚙️ **Automation**: Scheduled reminder system
- 🔌 **MCP Support**: Model Context Protocol integration
- 📆 **Google Calendar Sync**: Real appointments stored in Google Calendar

## Tech Stack

- **FastAPI**: Modern Python web framework
- **LangChain**: AI agent framework
- **Twilio**: Phone calls and MMS
- **Google Calendar API**: Official calendar integration
- **WebSockets**: Real-time communication
- **APScheduler**: Task scheduling

## Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Required configuration:
- `GROQ_API_KEY`: For AI agent (LLaMA via Groq)
- `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_PHONE_NUMBER`: For phone calls and MMS
- `GOOGLE_SERVICE_ACCOUNT_FILE`, `GOOGLE_CALENDAR_ID`: For Google Calendar sync
- (Optional) `GOOGLE_CALENDAR_DELEGATED_USER`, `CLINIC_TIMEZONE`

### 3. Run the Server

```bash
python main.py
```

Or with uvicorn:

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Chat
- `POST /api/chat/` - Send chat message
- `POST /api/chat/session/new` - Create new session
- `WebSocket /ws` - Real-time chat

### Appointments
- `GET /api/appointments/` - List appointments
- `GET /api/appointments/{id}` - Get appointment
- `POST /api/appointments/` - Create appointment
- `DELETE /api/appointments/{id}` - Cancel appointment
- `GET /api/appointments/availability/check` - Check availability
- `GET /api/appointments/availability/alternatives` - Get alternatives

### Phone
- `POST /api/phone/incoming` - Handle incoming call
- `POST /api/phone/process` - Process voice input
- `POST /api/phone/webhook` - Twilio webhook

## How It Works

### AI Agent Flow

1. **Collecting Name**: Agent asks for patient's full name
2. **Collecting Phone**: Agent asks for phone number
3. **Collecting DateTime**: Agent asks for preferred date and time
4. **Checking Availability**: Agent checks if time slot is available
5. **Confirming**: Agent confirms appointment details
6. **Booking**: Agent books the appointment in the calendar

### Reminder System

The scheduler runs every hour and checks for appointments that need reminders (24 hours before). It automatically sends MMS reminders to patients.

### Phone Integration

When a patient calls, Twilio routes the call to `/api/phone/incoming`. The AI agent processes speech input and responds with TwiML.

### Google Calendar Sync

Appointments are validated and stored in the configured Google Calendar using a service
account. Each booking step:

1. Checks Google Calendar for conflicts during the requested time
2. Creates the calendar event with patient details in the description/extended properties
3. Persists the event metadata (including `google_event_id`) inside the MCP store
4. Deletes the Google event automatically if the appointment is cancelled

Be sure the service account has write access to the target calendar. Optionally, set
`GOOGLE_CALENDAR_DELEGATED_USER` if your workspace requires domain-wide delegation.

## Development

### Project Structure

```
backend/
├── app/
│   ├── routers/          # API routes
│   ├── services/          # Business logic
│   ├── database.py        # Database models
│   └── config.py          # Configuration
├── main.py                # FastAPI app
└── requirements.txt       # Dependencies
```

## Notes

- The AI agent uses Groq's LLaMA 3 model by default (can be configured)
- MCP server is optional but recommended for enhanced context
- Appointment metadata lives in the MCP server; Google Calendar stores the actual events
- Reminder system runs automatically in the background

