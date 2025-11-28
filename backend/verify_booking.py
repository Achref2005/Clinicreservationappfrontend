"""
Quick script to verify appointments are being stored
"""
import asyncio
from app.services.calendar import CalendarService
from datetime import datetime, timedelta

async def verify_booking():
    calendar_service = CalendarService()
    
    print("=" * 50)
    print("Verifying Appointment Storage")
    print("=" * 50)
    
    # Check if Google Calendar is enabled
    if calendar_service.google_enabled:
        print("✅ Google Calendar is ENABLED")
        print(f"   Calendar ID: {calendar_service.google_calendar.calendar_id}")
    else:
        print("⚠️  Google Calendar is DISABLED")
        print("   To enable: Set GOOGLE_SERVICE_ACCOUNT_FILE and GOOGLE_CALENDAR_ID in .env")
    
    # Check MCP connection
    print("\n📡 Checking MCP Server...")
    try:
        # Try to get all appointments
        appointments = await calendar_service.get_all_appointments()
        print(f"✅ MCP Server is connected")
        print(f"   Found {len(appointments)} appointments in MCP database")
        
        if appointments:
            print("\n📅 Recent Appointments:")
            for apt in appointments[:5]:  # Show first 5
                print(f"   - {apt.get('patient_name')}: {apt.get('appointment_date')} at {apt.get('appointment_time')}")
        else:
            print("   No appointments found yet. Book one through the chatbot!")
    except Exception as e:
        print(f"❌ MCP Server connection failed: {e}")
        print("   Make sure MCP server is running at MCP_SERVER_URL")
    
    print("\n" + "=" * 50)
    print("Summary:")
    print("=" * 50)
    print("When you book an appointment:")
    print("1. ✅ Metadata is stored in MCP server (always)")
    print("2. " + ("✅" if calendar_service.google_enabled else "⚠️ ") + " Event is created in Google Calendar (if configured)")
    print("\nTo view appointments:")
    print("- Frontend: Visit /appointments page")
    print("- Backend API: GET /api/appointments/")
    print("- Google Calendar: Check your calendar if configured")

if __name__ == "__main__":
    asyncio.run(verify_booking())



