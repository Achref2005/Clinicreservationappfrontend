# Complete Setup Guide - Frontend & Backend

This guide will help you get both the frontend and backend running together.

## Prerequisites

- **Python 3.11+** installed
- **Node.js 18+** and npm installed
- **Groq API Key** (for AI agent) - Get from https://console.groq.com/
- **Google Calendar API** credentials (optional but recommended)
- **Twilio account** (optional, for phone/MMS features)

## Step 1: Backend Setup

### 1.1 Navigate to Backend Directory

```bash
cd backend
```

### 1.2 Create Virtual Environment (if not already done)

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

### 1.3 Install Dependencies

```bash
pip install -r requirements.txt
```

### 1.4 Configure Environment Variables

Create a `.env` file in the `backend` directory:

```bash
# Copy the example file
copy .env.example .env
```

Or create `.env` manually with:

```env
# Required for AI agent
GROQ_API_KEY=gsk_your_actual_key_here

# Required for Google Calendar sync
GOOGLE_SERVICE_ACCOUNT_FILE=service-account.json
GOOGLE_CALENDAR_ID=your_calendar_id@group.calendar.google.com

# Optional
GOOGLE_CALENDAR_DELEGATED_USER=
CLINIC_TIMEZONE=UTC

# Optional - for phone/MMS
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_PHONE_NUMBER=
```

**Note:** The app will work without `GROQ_API_KEY`, but AI responses will be less natural. Without Google Calendar credentials, appointments won't be saved to a real calendar.

### 1.5 Start the Backend Server

```bash
python main.py
```

Or use uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The backend should now be running at `http://localhost:8000`

**Verify it's working:**
- Open `http://localhost:8000/health` in your browser - should return `{"status": "healthy"}`
- Open `http://localhost:8000/docs` for API documentation

## Step 2: Frontend Setup

### 2.1 Navigate to Project Root

Open a **new terminal** (keep backend running) and navigate to the project root:

```bash
cd C:\Users\ashref\Desktop\Clinicreservationappfrontend
```

### 2.2 Install Dependencies

```bash
npm install
```

### 2.3 Configure Environment Variables

Create a `.env` file in the **project root** (same level as `package.json`):

```env
VITE_API_URL=http://localhost:8000
```

### 2.4 Start the Frontend

```bash
npm run dev
```

The frontend should now be running at `http://localhost:3000` (or `http://localhost:5173` depending on Vite config)

## Step 3: Test Everything

### 3.1 Test Backend API

Run the test script:
```bash
cd backend
python test_api.py
```

### 3.2 Test Frontend Connection

1. Open `http://localhost:3000` (or the port shown in terminal)
2. Navigate to the booking/chat page
3. Try sending a message - it should connect to the backend

### 3.3 Test WebSocket (Real-time Chat)

1. Open the chat interface in the frontend
2. Send a message - you should see responses in real-time

## Troubleshooting

### Backend Issues

**Error: "GROQ_API_KEY not found"**
- The app will still work, but AI responses will be basic
- Add your Groq API key to `backend/.env`

**Error: "Cannot connect to Google Calendar"**
- Make sure `service-account.json` exists in the `backend` directory
- Verify `GOOGLE_CALENDAR_ID` is correct
- Check that the service account has access to the calendar

**Error: "Module not found"**
- Make sure virtual environment is activated
- Run `pip install -r requirements.txt` again

**Port 8000 already in use**
- Change `PORT=8001` in `backend/.env`
- Update `VITE_API_URL=http://localhost:8001` in frontend `.env`

### Frontend Issues

**Error: "Cannot connect to API"**
- Make sure backend is running on port 8000
- Check `VITE_API_URL` in frontend `.env` matches backend port
- Check browser console for CORS errors

**CORS Errors**
- Backend CORS is configured for `localhost:3000` and `localhost:5173`
- If using a different port, add it to `backend/app/config.py` in `CORS_ORIGINS`

**npm install fails**
- Try deleting `node_modules` and `package-lock.json`, then run `npm install` again
- Make sure Node.js version is 18+

## Running Both Together

You need **two terminals**:

**Terminal 1 - Backend:**
```bash
cd backend
venv\Scripts\activate  # Windows
# or: source venv/bin/activate  # Mac/Linux
python main.py
```

**Terminal 2 - Frontend:**
```bash
cd C:\Users\ashref\Desktop\Clinicreservationappfrontend
npm run dev
```

## Quick Start Commands

**Windows - Backend:**
```powershell
cd backend
venv\Scripts\activate
python main.py
```

**Windows - Frontend:**
```powershell
npm run dev
```

## Next Steps

1. ✅ Both servers running
2. ✅ Test chat functionality
3. ✅ Test appointment booking
4. ✅ Configure Google Calendar (optional)
5. ✅ Set up Twilio for phone/MMS (optional)

## API Endpoints

- **Health Check:** `GET http://localhost:8000/health`
- **API Docs:** `http://localhost:8000/docs`
- **Chat:** `POST http://localhost:8000/api/chat/`
- **Appointments:** `GET http://localhost:8000/api/appointments/`
- **WebSocket:** `ws://localhost:8000/ws`

## Support

- Backend README: `backend/README.md`
- Project Setup: `PROJECT_SETUP.md`
- API Documentation: `http://localhost:8000/docs` (when backend is running)



