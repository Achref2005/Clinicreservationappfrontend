# Frontend Integration Guide

This guide shows how to connect the React frontend to the Python backend.

## Quick Start

1. **Update BookingPage.tsx** to use the API service:

```typescript
import { useState, useRef, useEffect } from 'react';
import { apiService, ChatResponse } from '../services/api';
// ... other imports

export function BookingPage() {
  const [messages, setMessages] = useState<Message[]>([...]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  // ... other state

  useEffect(() => {
    // Create session on mount
    apiService.createSession().then(id => setSessionId(id));
  }, []);

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      text: inputValue,
      sender: 'user',
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    const currentInput = inputValue;
    setInputValue('');

    try {
      // Call backend API
      const response: ChatResponse = await apiService.sendChatMessage(currentInput);
      
      const aiResponse: Message = {
        id: (Date.now() + 1).toString(),
        text: response.message,
        sender: 'assistant',
        timestamp: new Date(),
      };
      
      setMessages((prev) => [...prev, aiResponse]);
      
      // Handle appointment confirmation
      if (response.appointment_data) {
        // Show success message or redirect
        console.log('Appointment booked:', response.appointment_data);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      // Show error message to user
    }
  };

  // ... rest of component
}
```

2. **Update AppointmentsPage.tsx** to fetch real data:

```typescript
import { apiService, Appointment } from '../services/api';

export function AppointmentsPage() {
  // ... existing code

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      const appointments = await apiService.getAppointments(phone);
      setAppointments(appointments);
      setSearched(true);
    } catch (error) {
      console.error('Error fetching appointments:', error);
      // Show error to user
    }
  };

  // ... rest of component
}
```

## WebSocket Integration (Optional)

For real-time chat, you can use WebSocket:

```typescript
useEffect(() => {
  const ws = apiService.connectWebSocket(
    (data: ChatResponse) => {
      // Handle incoming message
      const aiResponse: Message = {
        id: Date.now().toString(),
        text: data.message,
        sender: 'assistant',
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, aiResponse]);
    },
    (error) => {
      console.error('WebSocket error:', error);
    }
  );

  return () => {
    ws.close();
  };
}, []);
```

## Environment Variables

Create a `.env` file in the frontend root:

```env
VITE_API_URL=http://localhost:8000
```

## CORS Configuration

The backend is configured to accept requests from:
- `http://localhost:5173` (Vite default)
- `http://localhost:3000` (React default)

If you're using a different port, update `CORS_ORIGINS` in `backend/app/config.py`.

## Testing

1. Start the backend:
   ```bash
   cd backend
   python main.py
   ```

2. Start the frontend:
   ```bash
   npm run dev
   ```

3. Test the chat interface - it should now connect to the real backend!





