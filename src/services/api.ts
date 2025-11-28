/**
 * API service for connecting to the backend
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface ChatMessage {
  message: string;
  session_id?: string;
}

export interface ChatResponse {
  message: string;
  session_id: string;
  appointment_data?: {
    id: number;
    date: string;
    time: string;
  };
}

export interface Appointment {
  id: number;
  patient_name: string;
  patient_phone: string;
  appointment_date: string;
  appointment_time: string;
  status: string;
  reminder_sent: boolean;
}

export interface Doctor {
  id: number;
  name: string;
  specialty: string;
  experience: string;
  qualifications: string;
  about: string;
}

class ApiService {
  private sessionId: string | null = null;

  async createSession(): Promise<string> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/chat/session/new`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });
      const data = await response.json();
      this.sessionId = data.session_id;
      return data.session_id;
    } catch (error) {
      console.error('Error creating session:', error);
      // Generate a local session ID as fallback
      this.sessionId = `session_${Date.now()}`;
      return this.sessionId;
    }
  }

  async sendChatMessage(message: string): Promise<ChatResponse> {
    if (!this.sessionId) {
      await this.createSession();
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/chat/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message,
          session_id: this.sessionId,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data: ChatResponse = await response.json();
      if (data.session_id) {
        this.sessionId = data.session_id;
      }
      return data;
    } catch (error) {
      console.error('Error sending chat message:', error);
      throw error;
    }
  }

  async getAppointments(phone?: string, date?: string): Promise<Appointment[]> {
    const params = new URLSearchParams();
    if (phone) params.append('phone', phone);
    if (date) params.append('date', date);

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/appointments/?${params.toString()}`,
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching appointments:', error);
      throw error;
    }
  }

  async checkAvailability(date: string, time: string): Promise<boolean> {
    try {
      const response = await fetch(
        `${API_BASE_URL}/api/appointments/availability/check?date=${date}&time=${time}`,
        {
          method: 'GET',
          headers: {
            'Content-Type': 'application/json',
          },
        }
      );

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data.available;
    } catch (error) {
      console.error('Error checking availability:', error);
      return false;
    }
  }

  connectWebSocket(
    onMessage: (data: ChatResponse) => void,
    onError?: (error: Event) => void
  ): WebSocket {
    const wsUrl = API_BASE_URL.replace('http', 'ws') + '/ws';
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      console.log('WebSocket connected');
    };

    ws.onmessage = (event) => {
      try {
        const data: ChatResponse = JSON.parse(event.data);
        onMessage(data);
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      if (onError) onError(error);
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
    };

    return ws;
  }

  async getDoctors(): Promise<Doctor[]> {
    try {
      const response = await fetch(`${API_BASE_URL}/api/doctors/`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error fetching doctors:', error);
      throw error;
    }
  }
}

export const apiService = new ApiService();



