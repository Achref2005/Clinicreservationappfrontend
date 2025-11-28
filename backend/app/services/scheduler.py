"""
Scheduler service for automated reminder sending.

All appointment data is retrieved and updated via the MCP server.
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta

from app.services.mms_service import MMSService
from app.services.mcp_client import MCPClient
from app.config import settings


class ReminderScheduler:
    """Scheduler for sending appointment reminders."""

    def __init__(self) -> None:
        self.scheduler = AsyncIOScheduler()
        self.mms_service = MMSService()
        self.mcp_client = MCPClient()
        self.running = False

    def start(self) -> None:
        """Start the scheduler."""
        if not self.running:
            # Run reminder check every hour
            self.scheduler.add_job(
                self.check_and_send_reminders,
                CronTrigger(minute=0),  # Run at the top of every hour
                id="reminder_check",
                replace_existing=True,
            )
            self.scheduler.start()
            self.running = True
            print("✅ Reminder scheduler started")

    def stop(self) -> None:
        """Stop the scheduler."""
        if self.running:
            self.scheduler.shutdown()
            self.running = False
            print("✅ Reminder scheduler stopped")

    async def check_and_send_reminders(self) -> None:
        """Check for appointments that need reminders and send them."""
        try:
            # Calculate the reminder time window
            now = datetime.now()
            reminder_window_start = now + timedelta(
                hours=settings.REMINDER_HOURS_BEFORE
            )
            reminder_window_end = reminder_window_start + timedelta(hours=1)

            # Ask MCP for appointments that need reminders in this window
            result = await self.mcp_client.execute_tool(
                "calendar.get_appointments_for_reminder",
                {
                    "window_start": reminder_window_start.isoformat(),
                    "window_end": reminder_window_end.isoformat(),
                },
            )

            appointments = result.get("result", {}).get("appointments", [])

            for appointment in appointments:
                # Expected appointment keys from MCP:
                # id, patient_name, patient_phone, appointment_date, appointment_time
                send_result = self.mms_service.send_reminder(
                    to_phone=appointment["patient_phone"],
                    patient_name=appointment["patient_name"],
                    appointment_date=datetime.fromisoformat(
                        appointment["appointment_date"]
                    ),
                    appointment_time=appointment["appointment_time"],
                )

                if send_result.get("success"):
                    # Tell MCP that reminder was sent
                    await self.mcp_client.execute_tool(
                        "calendar.mark_reminder_sent",
                        {"appointment_id": appointment["id"]},
                    )
                    print(
                        f"✅ Reminder sent to {appointment['patient_name']} "
                        f"for {appointment['appointment_date']}"
                    )
                else:
                    print(
                        f"❌ Failed to send reminder to {appointment['patient_name']}: "
                        f"{send_result.get('error')}"
                    )

        except Exception as e:
            print(f"❌ Error in reminder scheduler: {e}")

