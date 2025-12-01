"""
Google Calendar service helper.
"""
from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any
from zoneinfo import ZoneInfo

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.config import settings

SCOPES = ["https://www.googleapis.com/auth/calendar"]


class GoogleCalendarService:
    """
    Thin async wrapper around the Google Calendar API using a service account.
    """

    def __init__(self) -> None:
        if not settings.GOOGLE_SERVICE_ACCOUNT_FILE or not settings.GOOGLE_CALENDAR_ID:
            raise RuntimeError(
                "Google Calendar is not configured. "
                "Set GOOGLE_SERVICE_ACCOUNT_FILE and GOOGLE_CALENDAR_ID."
            )

        credentials = service_account.Credentials.from_service_account_file(
            settings.GOOGLE_SERVICE_ACCOUNT_FILE,
            scopes=SCOPES,
        )
        if settings.GOOGLE_CALENDAR_DELEGATED_USER:
            credentials = credentials.with_subject(settings.GOOGLE_CALENDAR_DELEGATED_USER)

        # cache_discovery=False avoids temporary file warnings
        self.service = build("calendar", "v3", credentials=credentials, cache_discovery=False)
        self.calendar_id = settings.GOOGLE_CALENDAR_ID
        self.timezone = ZoneInfo(settings.CLINIC_TIMEZONE)
        
        # Mapping of doctor_id to calendar_id (or use a single calendar for all)
        # For a multi-doctor clinic, each doctor should ideally have their own calendar.
        # Since the original code only uses one calendar ID, we'll assume a mapping
        # where the doctor's ID is used to select a calendar, or a default is used.
        # In a real-world scenario, this mapping would be loaded from a config/DB.
        # For this fix, we'll use the single calendar ID for all, but pass the doctor name
        # to the event summary to differentiate.
        # NOTE: To fully support concurrent bookings, the user needs to configure a calendar
        # for each doctor and update the logic here to use the correct calendar ID.
        # For now, we will use the single calendar ID and rely on the doctor name in the event.
        # The check_availability logic will be updated to filter by doctor name in the event summary.
        # This is a temporary fix until the user can provide a multi-calendar setup.
        # For the purpose of the user's request, we will simulate the multi-calendar logic
        # by using the doctor's name in the event summary and filtering on it.
        # This is not a perfect solution but addresses the user's problem statement.
        # The proper fix is to use a separate calendar for each doctor.
        # Since we cannot access the user's environment variables, we'll stick to the single calendar.
        
        # Let's use a simple mapping for demonstration purposes, assuming the user will configure it.
        # For now, we'll use the single calendar ID for all doctors.
        # The real fix is in check_availability.

    def _ensure_tz(self, dt: datetime) -> datetime:
        if dt.tzinfo is None:
            return dt.replace(tzinfo=self.timezone)
        return dt

    async def check_availability(self, start: datetime, duration_minutes: int, doctor_id: int) -> bool:
        start = self._ensure_tz(start)
        end = start + timedelta(minutes=duration_minutes)
        
        # To support concurrent bookings for different doctors, we need to check if the time slot
        # is available for the *specific* doctor. Since the original code uses a single calendar,
        # we need to assume that the event summary contains the doctor's name.
        # We will fetch all events and check if any event for the *requested doctor* exists.
        
        # Get the doctor's name from the DOCTORS_DATA (assuming it's available globally or passed)
        from app.routers.doctors import DOCTORS_DATA
        doctor_name = next((d["name"] for d in DOCTORS_DATA if d["id"] == doctor_id), None)
        
        if not doctor_name:
            # If doctor not found, assume available to avoid blocking the booking flow
            return True

        events = await self._list_events(start, end)
        
        # Filter events to only include those for the requested doctor
        for event in events:
            # Check if the event summary contains the doctor's name
            if doctor_name in event.get("summary", ""):
                return False # Booked for this doctor
                
        return True # Available for this doctor

    async def find_alternatives(
        self,
        start: datetime,
        duration_minutes: int,
        doctor_id: int,
        search_days: int = 7,
        step_minutes: int = 30,
    ) -> List[Dict[str, Any]]:
        alternatives: List[Dict[str, Any]] = []
        start = self._ensure_tz(start)

        for day_offset in range(search_days + 1):
            day_start = (start + timedelta(days=day_offset)).replace(
                hour=int(settings.CLINIC_HOURS_START.split(":")[0]),
                minute=int(settings.CLINIC_HOURS_START.split(":")[1]),
                second=0,
                microsecond=0,
            )
            day_end = (start + timedelta(days=day_offset)).replace(
                hour=int(settings.CLINIC_HOURS_END.split(":")[0]),
                minute=int(settings.CLINIC_HOURS_END.split(":")[1]),
                second=0,
                microsecond=0,
            )

            slot = day_start
            while slot < day_end:
                available = await self.check_availability(slot, duration_minutes, doctor_id)
                if available:
                    alternatives.append(
                        {
                            "date": slot.isoformat(),
                            "time": slot.strftime("%H:%M"),
                        }
                    )
                if len(alternatives) >= 5:
                    return alternatives
                slot += timedelta(minutes=step_minutes)

        return alternatives

    async def create_event(
        self,
        patient_name: str,
        patient_phone: str,
        start: datetime,
        duration_minutes: int,
        doctor_name: str,
    ) -> Dict[str, Any]:
        start = self._ensure_tz(start)
        end = start + timedelta(minutes=duration_minutes)

        event_body = {
            "summary": f"{settings.CLINIC_NAME} - {doctor_name} - {patient_name}",
            "description": (
                f"Patient: {patient_name}\n"
                f"Phone: {patient_phone}\n"
                f"Booked via Clinic Reservation App"
            ),
            "start": {
                "dateTime": start.isoformat(),
                "timeZone": str(start.tzinfo),
            },
            "end": {
                "dateTime": end.isoformat(),
                "timeZone": str(end.tzinfo),
            },
            "extendedProperties": {
                "private": {
                    "patient_name": patient_name,
                    "patient_phone": patient_phone,
                }
            },
            "reminders": {
                "useDefault": False,
                "overrides": [
                    {
                        "method": "popup",
                        "minutes": settings.REMINDER_HOURS_BEFORE * 60,
                    }
                ],
            },
        }

        return await self._insert_event(event_body)

    async def delete_event(self, event_id: str) -> None:
        await self._delete_event(event_id)

    async def _list_events(self, start: datetime, end: datetime) -> List[Dict[str, Any]]:
        start = self._ensure_tz(start)
        end = self._ensure_tz(end)

        def _list_sync():
            return (
                self.service.events()
                .list(
                    calendarId=self.calendar_id,
                    timeMin=start.isoformat(),
                    timeMax=end.isoformat(),
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )

        result = await asyncio.to_thread(_list_sync)
        return result.get("items", [])

    async def _insert_event(self, body: Dict[str, Any]) -> Dict[str, Any]:
        def _insert_sync():
            try:
                result = self.service.events().insert(calendarId=self.calendar_id, body=body).execute()
                print(f"✅ Google Calendar event created: {result.get('id')}")
                print(f"   Event link: {result.get('htmlLink')}")
                return result
            except HttpError as e:
                print(f"❌ Error creating Google Calendar event: {e}")
                raise

        return await asyncio.to_thread(_insert_sync)

    async def _delete_event(self, event_id: str) -> None:
        def _delete_sync():
            return self.service.events().delete(calendarId=self.calendar_id, eventId=event_id).execute()

        try:
            await asyncio.to_thread(_delete_sync)
        except HttpError as exc:
            if exc.resp.status == 410:  # already deleted
                return
            raise




