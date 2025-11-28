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

    def _ensure_tz(self, dt: datetime) -> datetime:
        if dt.tzinfo is None:
            return dt.replace(tzinfo=self.timezone)
        return dt

    async def check_availability(self, start: datetime, duration_minutes: int) -> bool:
        start = self._ensure_tz(start)
        end = start + timedelta(minutes=duration_minutes)
        events = await self._list_events(start, end)
        return len(events) == 0

    async def find_alternatives(
        self,
        start: datetime,
        duration_minutes: int,
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
                available = await self.check_availability(slot, duration_minutes)
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
    ) -> Dict[str, Any]:
        start = self._ensure_tz(start)
        end = start + timedelta(minutes=duration_minutes)

        event_body = {
            "summary": f"{settings.CLINIC_NAME} - {patient_name}",
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




