"""
Diagnostic script to check booking issues
"""
import asyncio
from app.services.calendar import CalendarService
from app.config import settings
from datetime import datetime, timedelta

async def diagnose():
    print("=" * 60)
    print("Booking System Diagnostic")
    print("=" * 60)
    
    calendar_service = CalendarService()
    
    # 1. Check Google Calendar
    print("\n1. Google Calendar Status:")
    if calendar_service.google_enabled:
        print("   ✅ Google Calendar is ENABLED")
        print(f"   Calendar ID: {calendar_service.google_calendar.calendar_id}")
    else:
        print("   ⚠️  Google Calendar is DISABLED")
        print("   Reason: Check backend startup logs")
        print("   To enable: Set GOOGLE_SERVICE_ACCOUNT_FILE and GOOGLE_CALENDAR_ID")
    
    # 2. Check MCP Connection
    print("\n2. MCP Server Status:")
    try:
        appointments = await calendar_service.get_all_appointments()
        print(f"   ✅ MCP Server is connected")
        print(f"   Found {len(appointments)} appointments")
        
        if appointments:
            print("\n   Recent Appointments:")
            for apt in appointments[:5]:
                print(f"   - ID: {apt.get('id')}")
                print(f"     Patient: {apt.get('patient_name')}")
                print(f"     Phone: {apt.get('patient_phone')}")
                print(f"     Date: {apt.get('appointment_date')}")
                print(f"     Time: {apt.get('appointment_time')}")
                print(f"     Google Event ID: {apt.get('google_event_id', 'None')}")
                print()
        else:
            print("   ⚠️  No appointments found in MCP")
            print("   This could mean:")
            print("   - No appointments have been booked yet")
            print("   - MCP server is not storing appointments correctly")
            print("   - MCP server needs to be restarted")
    except Exception as e:
        print(f"   ❌ MCP Server connection failed: {e}")
        import traceback
        traceback.print_exc()
    
    # 3. Test API endpoint
    print("\n3. API Endpoint Test:")
    print("   Test by running: curl http://localhost:8000/api/appointments/")
    print("   Or visit: http://localhost:8000/api/appointments/")
    
    # 4. Configuration check
    print("\n4. Configuration:")
    print(f"   MCP_SERVER_URL: {settings.MCP_SERVER_URL}")
    print(f"   GOOGLE_CALENDAR_ID: {settings.GOOGLE_CALENDAR_ID or 'Not set'}")
    print(f"   GOOGLE_SERVICE_ACCOUNT_FILE: {settings.GOOGLE_SERVICE_ACCOUNT_FILE or 'Not set'}")
    
    print("\n" + "=" * 60)
    print("Next Steps:")
    print("=" * 60)
    print("1. Check backend logs when booking an appointment")
    print("2. Verify MCP server is running at:", settings.MCP_SERVER_URL)
    print("3. If Google Calendar not working, check service account file exists")
    print("4. Test booking an appointment and watch the logs")

if __name__ == "__main__":
    asyncio.run(diagnose())



