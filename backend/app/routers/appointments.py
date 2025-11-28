"""
Appointments API router (MCP-backed, no local database).
"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from app.services.calendar import CalendarService

router = APIRouter()
calendar_service = CalendarService()


class AppointmentResponse(BaseModel):
    id: int
    patient_name: str
    patient_phone: str
    appointment_date: str
    appointment_time: str
    status: str
    reminder_sent: bool | None = None


class AppointmentCreate(BaseModel):
    patient_name: str
    patient_phone: str
    appointment_date: str  # ISO format
    appointment_time: str


@router.get("/", response_model=List[AppointmentResponse])
async def get_appointments(
    phone: Optional[str] = None,
    date: Optional[str] = None,
):
    """Get appointments, optionally filtered by phone or date (data from MCP)."""
    try:
        if phone:
            print(f"📞 Fetching appointments for phone: {phone}")
            appointments = await calendar_service.get_appointments_by_phone(phone)
        elif date:
            print(f"📅 Fetching appointments for date: {date}")
            date_obj = datetime.fromisoformat(date)
            appointments = await calendar_service.get_appointments_by_date(date_obj)
        else:
            print("📋 Fetching all appointments")
            appointments = await calendar_service.get_all_appointments()

        print(f"✅ Returning {len(appointments)} appointments")
        return appointments
    except Exception as e:
        print(f"❌ Error in get_appointments: {e}")
        import traceback
        traceback.print_exc()
        return []


@router.get("/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(appointment_id: int):
    """Get a specific appointment by ID (via MCP)."""
    # Re-use the generic getter and filter client-side for simplicity.
    appointments = await calendar_service.get_all_appointments()
    for apt in appointments:
        if apt.get("id") == appointment_id:
            return apt

    raise HTTPException(status_code=404, detail="Appointment not found")


@router.post("/", response_model=AppointmentResponse)
async def create_appointment(appointment: AppointmentCreate):
    """Create a new appointment via MCP."""
    appointment_date = datetime.fromisoformat(appointment.appointment_date)

    # Check availability
    is_available = await calendar_service.check_availability(
        appointment_date, appointment.appointment_time
    )

    if not is_available:
        raise HTTPException(status_code=400, detail="Time slot not available")

    # Book appointment
    booked = await calendar_service.book_appointment(
        patient_name=appointment.patient_name,
        patient_phone=appointment.patient_phone,
        appointment_date=appointment_date,
        appointment_time=appointment.appointment_time,
    )

    if not booked:
        raise HTTPException(status_code=400, detail="Failed to book appointment")

    return booked


@router.delete("/{appointment_id}")
async def cancel_appointment(appointment_id: int):
    """Cancel an appointment via MCP."""
    success = await calendar_service.cancel_appointment(appointment_id)

    if not success:
        raise HTTPException(status_code=404, detail="Appointment not found")

    return {"message": "Appointment cancelled successfully"}


@router.get("/availability/check")
async def check_availability(date: str, time: str):
    """Check if a time slot is available (MCP-backed)."""
    appointment_date = datetime.fromisoformat(date)
    is_available = await calendar_service.check_availability(appointment_date, time)

    return {
        "available": is_available,
        "date": date,
        "time": time,
    }


@router.get("/availability/alternatives")
async def get_alternatives(date: str, time: str):
    """Get alternative available time slots (MCP-backed)."""
    appointment_date = datetime.fromisoformat(date)
    alternatives = await calendar_service.find_alternatives(appointment_date, time)

    return {
        "alternatives": alternatives,
    }

