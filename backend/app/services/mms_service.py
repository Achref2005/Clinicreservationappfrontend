"""
MMS service for sending appointment reminders via multimedia messaging
"""
from twilio.rest import Client
from twilio.base.exceptions import TwilioException
from typing import Optional, Dict, Any
from datetime import datetime
from app.config import settings

class MMSService:
    """Service for sending MMS reminders"""
    
    def __init__(self):
        if settings.TWILIO_ACCOUNT_SID and settings.TWILIO_AUTH_TOKEN:
            self.client = Client(
                settings.TWILIO_ACCOUNT_SID,
                settings.TWILIO_AUTH_TOKEN
            )
            self.from_number = settings.TWILIO_PHONE_NUMBER
        else:
            self.client = None
            self.from_number = None
            print("⚠️ Twilio credentials not configured. MMS functionality will be limited.")
    
    def send_reminder(
        self,
        to_phone: str,
        patient_name: str,
        appointment_date: datetime,
        appointment_time: str
    ) -> Dict[str, Any]:
        """Send appointment reminder via MMS"""
        if not self.client:
            return {
                "success": False,
                "message": "MMS service not configured",
                "error": "Twilio credentials missing"
            }
        
        try:
            # Format appointment date
            date_str = appointment_date.strftime("%A, %B %d, %Y")
            
            # Create reminder message
            message_body = f"""
Hello {patient_name},

This is a reminder from {settings.CLINIC_NAME} about your upcoming appointment:

📅 Date: {date_str}
🕐 Time: {appointment_time}

Please arrive 10 minutes early. If you need to reschedule, please contact us.

We look forward to seeing you!

Best regards,
{settings.CLINIC_NAME}
            """.strip()
            
            # Send MMS (Twilio supports MMS when media_url is provided)
            # For text-only, we'll use SMS, but the service supports MMS
            message = self.client.messages.create(
                body=message_body,
                from_=self.from_number,
                to=to_phone
            )
            
            return {
                "success": True,
                "message": "Reminder sent successfully",
                "message_sid": message.sid,
                "status": message.status
            }
        
        except TwilioException as e:
            return {
                "success": False,
                "message": "Failed to send reminder",
                "error": str(e)
            }
        except Exception as e:
            return {
                "success": False,
                "message": "Unexpected error",
                "error": str(e)
            }
    
    def send_mms_with_image(
        self,
        to_phone: str,
        message_body: str,
        media_url: str
    ) -> Dict[str, Any]:
        """Send MMS with image attachment"""
        if not self.client:
            return {
                "success": False,
                "message": "MMS service not configured"
            }
        
        try:
            message = self.client.messages.create(
                body=message_body,
                from_=self.from_number,
                to=to_phone,
                media_url=[media_url]  # List of media URLs for MMS
            )
            
            return {
                "success": True,
                "message": "MMS sent successfully",
                "message_sid": message.sid
            }
        except Exception as e:
            return {
                "success": False,
                "message": "Failed to send MMS",
                "error": str(e)
            }



