# Clinic Reservation App - Complete Setup Guide

This guide will help you set up both the frontend and backend for the Clinic Reservation App.

## Project Overview

The Clinic Reservation App consists of:
- **Frontend**: React + TypeScript + Vite (already created)
- **Backend**: Python + FastAPI + AI Agent + MCP + Automation + MMS

## Prerequisites

- Node.js 18+ and npm
- Python 3.10+
- Groq API key (for AI agent – LLaMA models)
- Twilio account (for phone calls and MMS) - Optional but recommended
- Google Cloud project with a service account that can access your clinic calendar

## Backend Setup

### 1. Navigate to Backend Directory

```bash
cd backend
```

### 2. Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Mac/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env` and add your credentials:

```env
# Required
GROQ_API_KEY=gsk_your_key_here
GOOGLE_SERVICE_ACCOUNT_FILE=service-account.json
GOOGLE_CALENDAR_ID=your_calendar_id@group.calendar.google.com

# Optional
GOOGLE_CALENDAR_DELEGATED_USER=
CLINIC_TIMEZONE=UTC

# Optional (for phone/MMS features)
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_PHONE_NUMBER=+1234567890
```

### 5. Start Backend Server

```bash
python main.py
```

Or use the startup script:
- Windows: `start.bat`
- Mac/Linux: `chmod +x start.sh && ./start.sh`

The backend will run on `http://localhost:8000`

## Frontend Setup

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure API URL

Create a `.env` file in the frontend root:

```env
VITE_API_URL=http://localhost:8000
```

### 3. Update BookingPage (Optional)

The frontend currently uses mock data. To connect to the backend:

1. The API service is already created in `src/services/api.ts`
2. Update `src/components/BookingPage.tsx` to use `apiService` instead of mock responses
3. See `FRONTEND_INTEGRATION.md` for detailed instructions

### 4. Start Frontend

```bash
npm run dev
```

The frontend will run on `http://localhost:5173`

## Features

### ✅ Implemented

- **AI Agent**: Natural language conversation for booking
- **Calendar System**: Appointment scheduling with availability checking
- **WebSocket Chat**: Real-time chat interface
- **Phone Integration**: Voice interactions via Twilio
- **MMS Reminders**: Automated appointment reminders
- **Automation**: Scheduled reminder system
- **MCP Support**: Model Context Protocol integration
- **Google Calendar Sync**: Real appointments read/write from Google Calendar

### 🔄 How It Works

1. **Patient Interaction**:
   - Patient chats with AI agent (via web or phone)
   - AI collects: name, phone, preferred date/time

2. **Availability Check**:
   - AI checks if requested time is available
   - If not, suggests alternatives

3. **Booking**:
   - Patient confirms appointment
   - AI books it in the calendar

4. **Reminders**:
   - Automated system sends MMS reminder 24 hours before appointment

## API Endpoints

### Chat
- `POST /api/chat/` - Send chat message
- `WebSocket /ws` - Real-time chat

### Appointments
- `GET /api/appointments/` - List appointments
- `POST /api/appointments/` - Create appointment
- `GET /api/appointments/availability/check` - Check availability

### Phone
- `POST /api/phone/incoming` - Handle incoming call

## Testing

### Test Chat API

```bash
curl -X POST http://localhost:8000/api/chat/ \
  -H "Content-Type: application/json" \
  -d '{"message": "My name is John Smith"}'
```

### Test WebSocket

Use a WebSocket client or the frontend chat interface.

### Test Phone (Requires Twilio)

1. Configure Twilio webhook: `http://your-domain.com/api/phone/incoming`
2. Call your Twilio number
3. Follow the voice prompts

## Troubleshooting

### Backend Issues

1. **Import errors**: Make sure virtual environment is activated
2. **Google auth errors**: Confirm the service-account file path and calendar ID
3. **Groq errors**: Check your API key in `.env`

### Frontend Issues

1. **CORS errors**: Check `CORS_ORIGINS` in backend config
2. **Connection errors**: Verify backend is running on port 8000
3. **API errors**: Check browser console for details

## Next Steps

1. Set up Twilio for phone/MMS features
2. Configure MCP server (optional)
3. Update frontend to use real API (see `FRONTEND_INTEGRATION.md`)
4. Deploy to production

## Support

For questions or issues, check:
- Backend README: `backend/README.md`
- Frontend Integration: `FRONTEND_INTEGRATION.md`
- API Documentation: `http://localhost:8000/docs` (when backend is running)

