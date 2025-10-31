"""
Twilio Service
Handles SMS notifications and reminders
"""

from twilio.rest import Client
from typing import Dict
from config import Config
from datetime import datetime

class TwilioService:
    """Service for SMS notifications via Twilio"""
    
    def __init__(self):
        self.client = None
        
        if Config.TWILIO_ACCOUNT_SID and Config.TWILIO_AUTH_TOKEN:
            try:
                self.client = Client(Config.TWILIO_ACCOUNT_SID, Config.TWILIO_AUTH_TOKEN)
                print("✅ Twilio client initialized")
            except Exception as e:
                print(f"⚠️ Twilio initialization failed: {e}")
        else:
            print("⚠️ Twilio credentials not configured. SMS features disabled.")
    
    def send_daily_reminder(self, phone_number: str, username: str) -> Dict:
        """Send daily reminder to log health data"""
        if not self.client:
            return {"success": False, "message": "SMS service not configured"}
        
        message_body = f"""
🩺 Health Tracker Pro Reminder

Hi {username}! 👋

Don't forget to log your health stats today:
📊 Steps
🔥 Calories
💓 Heart rate
😴 Sleep hours
💧 Water intake

Keep up your streak! 🔥

- Health Tracker Pro Team
        """.strip()
        
        return self._send_sms(phone_number, message_body)
    
    def send_weekly_summary(self, phone_number: str, username: str, stats: Dict) -> Dict:
        """Send weekly summary of health stats"""
        if not self.client:
            return {"success": False, "message": "SMS service not configured"}
        
        message_body = f"""
📊 Weekly Health Summary

Hi {username}! Here's your weekly progress:

📈 Avg Steps: {stats.get('avg_steps', 0):,}
🔥 Avg Calories: {stats.get('avg_calories', 0):,}
💓 Avg Heart Rate: {stats.get('avg_heart_rate', 0)} bpm
😴 Avg Sleep: {stats.get('avg_sleep', 0)} hrs
💧 Avg Water: {stats.get('avg_water', 0)} glasses

Great work! Keep it up! 💪

- Health Tracker Pro
        """.strip()
        
        return self._send_sms(phone_number, message_body)
    
    def send_milestone_alert(self, phone_number: str, username: str, milestone: str) -> Dict:
        """Send milestone achievement alert"""
        if not self.client:
            return {"success": False, "message": "SMS service not configured"}
        
        message_body = f"""
🎉 Congratulations {username}!

You've achieved a new milestone:
{milestone}

Keep crushing your health goals! 💪

- Health Tracker Pro
        """.strip()
        
        return self._send_sms(phone_number, message_body)
    
    def send_streak_reminder(self, phone_number: str, username: str, streak: int) -> Dict:
        """Send streak reminder"""
        if not self.client:
            return {"success": False, "message": "SMS service not configured"}
        
        message_body = f"""
🔥 Streak Alert!

Amazing {username}! You're on a {streak}-day streak! 🎯

Don't break the chain - log your health data today!

- Health Tracker Pro
        """.strip()
        
        return self._send_sms(phone_number, message_body)
    
    def _send_sms(self, to_number: str, body: str) -> Dict:
        """Internal method to send SMS"""
        try:
            message = self.client.messages.create(
                body=body,
                from_=Config.TWILIO_PHONE_NUMBER,
                to=to_number
            )
            
            return {
                "success": True,
                "message": "SMS sent successfully",
                "sid": message.sid
            }
            
        except Exception as e:
            print(f"Error sending SMS: {e}")
            return {
                "success": False,
                "message": f"Failed to send SMS: {str(e)}"
            }

