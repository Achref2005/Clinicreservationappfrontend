"""
Configuration settings for the application
"""
from pydantic_settings import BaseSettings
from typing import List
import os
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Server settings
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8000))
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    
    # CORS settings
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
    ]
    
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./clinic_reservations.db")
    
    # Groq / LLaMA settings
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")  # Configurable model
    
    # Twilio settings (for phone calls and MMS)
    TWILIO_ACCOUNT_SID: str = os.getenv("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN: str = os.getenv("TWILIO_AUTH_TOKEN", "")
    TWILIO_PHONE_NUMBER: str = os.getenv("TWILIO_PHONE_NUMBER", "")
    
    # MCP settings
    MCP_SERVER_URL: str = os.getenv("MCP_SERVER_URL", "http://localhost:3001")
    
    # Clinic settings
    CLINIC_NAME: str = "MediCare Clinic"
    CLINIC_HOURS_START: str = "09:00"
    CLINIC_HOURS_END: str = "17:00"
    APPOINTMENT_DURATION_MINUTES: int = 30
    
    # Reminder settings
    REMINDER_HOURS_BEFORE: int = 24  # Send reminder 24 hours before appointment
    
    # Google Calendar settings
    GOOGLE_CALENDAR_ID: str = os.getenv("GOOGLE_CALENDAR_ID", "")
    GOOGLE_SERVICE_ACCOUNT_FILE: str = os.getenv("GOOGLE_SERVICE_ACCOUNT_FILE", "")
    GOOGLE_CALENDAR_DELEGATED_USER: str = os.getenv("GOOGLE_CALENDAR_DELEGATED_USER", "")
    CLINIC_TIMEZONE: str = os.getenv("CLINIC_TIMEZONE", "UTC")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

