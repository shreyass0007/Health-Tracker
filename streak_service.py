"""
Streak Service
Tracks user login streaks using Pixela API or internal tracking
"""

import requests
from datetime import datetime, timedelta
from typing import Dict, Optional
from config import Config
from db_manager import DatabaseManager

class StreakService:
    """Service for tracking user login streaks"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.use_pixela = Config.is_feature_enabled('pixela_tracking')
        
        if self.use_pixela:
            self.pixela_username = Config.PIXELA_USERNAME
            self.pixela_token = Config.PIXELA_TOKEN
            self.pixela_base_url = "https://pixe.la/v1/users"
            print("✅ Pixela tracking enabled")
        else:
            print("ℹ️ Using internal streak tracking")
    
    def record_login(self, user_id: str) -> Dict:
        """Record a login and update streak"""
        today = datetime.utcnow().date()
        streak_data = self.db.get_streak(user_id)
        
        if not streak_data:
            # First login ever
            new_streak = {
                "user_id": user_id,
                "current_streak": 1,
                "longest_streak": 1,
                "last_login": datetime.utcnow(),
                "login_dates": [today.isoformat()]
            }
            self.db.upsert_streak(user_id, new_streak)
            
            # Also record in Pixela if enabled
            if self.use_pixela:
                self._record_pixela_login(user_id)
            
            return {"success": True, "streak": 1}
        
        last_login_date = streak_data['last_login'].date()
        
        # Check if already logged in today
        if last_login_date == today:
            return {"success": True, "streak": streak_data['current_streak'], "already_logged": True}
        
        # Calculate new streak
        yesterday = today - timedelta(days=1)
        
        if last_login_date == yesterday:
            # Consecutive day - increment streak
            new_current_streak = streak_data['current_streak'] + 1
        else:
            # Streak broken - reset to 1
            new_current_streak = 1
        
        # Update longest streak if current exceeds it
        new_longest_streak = max(streak_data['longest_streak'], new_current_streak)
        
        # Update login dates (keep last 365 days)
        login_dates = streak_data.get('login_dates', [])
        login_dates.append(today.isoformat())
        login_dates = login_dates[-365:]  # Keep only last year
        
        updated_streak = {
            "user_id": user_id,
            "current_streak": new_current_streak,
            "longest_streak": new_longest_streak,
            "last_login": datetime.utcnow(),
            "login_dates": login_dates
        }
        
        self.db.upsert_streak(user_id, updated_streak)
        
        # Record in Pixela if enabled
        if self.use_pixela:
            self._record_pixela_login(user_id)
        
        return {
            "success": True,
            "streak": new_current_streak,
            "is_new_record": new_current_streak == new_longest_streak and new_current_streak > 1
        }
    
    def get_streak(self, user_id: str) -> Optional[Dict]:
        """Get current streak data"""
        return self.db.get_streak(user_id)
    
    def _record_pixela_login(self, user_id: str) -> bool:
        """Record login in Pixela (if enabled)"""
        if not self.use_pixela:
            return False
        
        try:
            # Create a graph for this user if not exists
            graph_id = f"user_{user_id[:8]}"  # Use first 8 chars of user_id
            today = datetime.utcnow().strftime("%Y%m%d")
            
            # Try to update pixel (create if doesn't exist)
            url = f"{self.pixela_base_url}/{self.pixela_username}/graphs/{graph_id}"
            
            headers = {
                "X-USER-TOKEN": self.pixela_token
            }
            
            data = {
                "date": today,
                "quantity": "1"
            }
            
            response = requests.post(url, json=data, headers=headers)
            
            return response.status_code in [200, 201]
            
        except Exception as e:
            print(f"Pixela recording error: {e}")
            return False
    
    def get_streak_calendar(self, user_id: str, days: int = 30) -> Dict:
        """Get calendar view of login streak"""
        streak_data = self.db.get_streak(user_id)
        
        if not streak_data:
            return {"dates": [], "has_login": []}
        
        login_dates = set(streak_data.get('login_dates', []))
        
        # Generate last N days
        today = datetime.utcnow().date()
        calendar = []
        
        for i in range(days - 1, -1, -1):
            date = today - timedelta(days=i)
            calendar.append({
                "date": date.isoformat(),
                "logged_in": date.isoformat() in login_dates
            })
        
        return calendar
