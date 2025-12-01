"""
Calendar service that syncs MCP metadata with Google Calendar.
"""
from datetime import datetime
from typing import List, Dict, Optional

from app.config import settings
from app.services.mcp_client import MCPClient
from app.services.google_calendar import GoogleCalendarService


class CalendarService:
    """
    Manage appointments by writing to Google Calendar and storing metadata in MCP.
    """

    def __init__(self) -> None:
        self.mcp_client = MCPClient()
        try:
            self.google_calendar = GoogleCalendarService()
            self.google_enabled = True
            print(f"✅ Google Calendar enabled: {self.google_calendar.calendar_id}")
        except Exception as exc:  # pylint: disable=broad-except
            self.google_calendar = None
            self.google_enabled = False
            print(f"⚠️  Google Calendar disabled: {exc}")
            print(f"   To enable: Set GOOGLE_SERVICE_ACCOUNT_FILE and GOOGLE_CALENDAR_ID in .env")

    # ------------------------------------------------------------------ #
    # Helpers
    # ------------------------------------------------------------------ #
    def _within_clinic_hours(self, dt: datetime) -> bool:
        start_time = datetime.strptime(settings.CLINIC_HOURS_START, "%H:%M").time()
        end_time = datetime.strptime(settings.CLINIC_HOURS_END, "%H:%M").time()
        appt_time = dt.time()
        return start_time <= appt_time <= end_time

    async def _get_mcp_appointment(self, appointment_id: int) -> Optional[Dict]:
        """Fetch a single appointment from MCP."""
        result = await self.mcp_client.execute_tool(
            "calendar.get_appointment",
            {"appointment_id": appointment_id},
        )
        return result.get("result")

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #
    async def check_availability(self, date: datetime, time: str, doctor_id: int) -> bool:
        """Check if a specific date and time slot is available for a given doctor."""
        hour, minute = map(int, time.split(":"))
        appointment_datetime = date.replace(
            hour=hour, minute=minute, second=0, microsecond=0
        )

        if not self._within_clinic_hours(appointment_datetime):
            return False

        # Check Google Calendar first when available
        if self.google_enabled:
            google_available = await self.google_calendar.check_availability(
                appointment_datetime, settings.APPOINTMENT_DURATION_MINUTES, doctor_id
            )
            if not google_available:
                return False

        # Ask MCP to ensure metadata does not already have the slot
        result = await self.mcp_client.execute_tool(
            "calendar.check_availability",
            {
                "date": appointment_datetime.isoformat(),
                "time": time,
                "doctor_id": doctor_id,
            },
        )

        return bool(result.get("result", {}).get("available", True))

    async def find_alternatives(self, date: datetime, time: str, doctor_id: int) -> List[Dict]:
        """Find alternative available time slots for a given doctor."""
        hour, minute = map(int, time.split(":"))
        requested_dt = date.replace(hour=hour, minute=minute, second=0, microsecond=0)

        if self.google_enabled:
            return await self.google_calendar.find_alternatives(
                requested_dt,
                settings.APPOINTMENT_DURATION_MINUTES,
                doctor_id,
            )

        # Fallback to MCP-powered suggestions
        result = await self.mcp_client.execute_tool(
            "calendar.find_alternatives",
            {
                "requested_date": requested_dt.isoformat(),
                "requested_time": time,
                "clinic_hours_start": settings.CLINIC_HOURS_START,
                "clinic_hours_end": settings.CLINIC_HOURS_END,
                "appointment_duration_minutes": settings.APPOINTMENT_DURATION_MINUTES,
            },
        )
        return result.get("result", {}).get("alternatives", [])

    async def book_appointment(
        self,
        patient_name: str,
        patient_phone: str,
        appointment_date: datetime,
        appointment_time: str,
        doctor_id: int,
        doctor_name: str,
    ) -> Optional[Dict]:
        """Book an appointment in Google Calendar and store metadata in MCP."""
        if not await self.check_availability(appointment_date, appointment_time, doctor_id):
            return None

        hour, minute = map(int, appointment_time.split(":"))
        appointment_datetime = appointment_date.replace(
            hour=hour, minute=minute, second=0, microsecond=0
        )

        google_event = None
        if self.google_enabled:
            try:
                print(f"📅 Creating Google Calendar event...")
                google_event = await self.google_calendar.create_event(
                    patient_name=patient_name,
                    patient_phone=patient_phone,
                    start=appointment_datetime,
                    duration_minutes=settings.APPOINTMENT_DURATION_MINUTES,
                    doctor_name=doctor_name,
                )
                print(f"✅ Google Calendar event created successfully")
            except Exception as e:
                print(f"❌ Failed to create Google Calendar event: {e}")
                import traceback
                traceback.print_exc()
                # Continue with MCP storage even if Google Calendar fails

        payload = {
            "patient_name": patient_name,
            "patient_phone": patient_phone,
            "appointment_datetime": appointment_datetime.isoformat(),
            "appointment_time": appointment_time,
            "doctor_id": doctor_id,
            "doctor_name": doctor_name,
            "google_event_id": google_event.get("id") if google_event else None,
            "google_event_link": google_event.get("htmlLink") if google_event else None,
        }

        result = await self.mcp_client.execute_tool(
            "calendar.book_appointment",
            payload,
        )

        stored = result.get("result")
        
        # Log the booking result
        if stored:
            print(f"✅ Appointment booked successfully:")
            print(f"   Patient: {patient_name}")
            print(f"   Date: {appointment_datetime}")
            print(f"   MCP stored: {stored.get('id') if stored else 'No ID'}")
            if google_event:
                print(f"   Google Calendar event: {google_event.get('id')}")
        else:
            print(f"❌ Failed to store appointment in MCP")
            print(f"   MCP result: {result}")
            if google_event:
                # Rollback google event if MCP failed
                print(f"   Rolling back Google Calendar event...")
                await self.google_calendar.delete_event(google_event["id"])
        
        return stored

    async def get_appointments_by_date(self, date: datetime) -> List[Dict]:
        result = await self.mcp_client.execute_tool(
            "calendar.get_appointments_by_date",
            {"date": date.date().isoformat()},
        )
        return result.get("result", {}).get("appointments", [])

    async def get_appointments_by_phone(self, phone: str) -> List[Dict]:
        result = await self.mcp_client.execute_tool(
            "calendar.get_appointments_by_phone",
            {"phone": phone},
        )
        return result.get("result", {}).get("appointments", [])

    async def get_all_appointments(self) -> List[Dict]:
        result = await self.mcp_client.execute_tool(
            "calendar.get_all_appointments",
            {},
        )
        return result.get("result", {}).get("appointments", [])

    async def cancel_appointment(self, appointment_id: int) -> bool:
        """Cancel both the Google event and the MCP record."""
        appointment = await self._get_mcp_appointment(appointment_id)
        google_event_id = appointment.get("google_event_id") if appointment else None

        if self.google_enabled and google_event_id:
            await self.google_calendar.delete_event(google_event_id)

        result = await self.mcp_client.execute_tool(
            "calendar.cancel_appointment",
            {"appointment_id": appointment_id},
        )
        return bool(result.get("result", {}).get("success", False))

