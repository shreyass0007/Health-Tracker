"""
Helper Utilities
Common utility functions
"""

from datetime import datetime, timedelta
from typing import List, Dict
import pandas as pd
from bson import ObjectId

class Helpers:
    """Helper utility functions"""
    
    @staticmethod
    def format_date(date: datetime, format_str: str = "%Y-%m-%d") -> str:
        """Format datetime object"""
        return date.strftime(format_str)
    
    @staticmethod
    def get_date_range(days: int) -> List[datetime]:
        """Get list of dates for the last N days"""
        today = datetime.utcnow()
        return [today - timedelta(days=i) for i in range(days-1, -1, -1)]
    
    @staticmethod
    def calculate_percentage(value: float, target: float) -> float:
        """Calculate percentage of target achieved"""
        if target == 0:
            return 0
        return min((value / target) * 100, 100)
    
    @staticmethod
    def get_health_status(score: int) -> tuple:
        """Get health status based on score"""
        if score >= 80:
            return ("Excellent", "🟢", "Your health metrics are outstanding!")
        elif score >= 60:
            return ("Good", "🟡", "You're doing well! Keep it up.")
        elif score >= 40:
            return ("Fair", "🟠", "Room for improvement. You can do better!")
        else:
            return ("Needs Attention", "🔴", "Focus on improving your health habits.")
    
    @staticmethod
    def entries_to_dataframe(entries: List[Dict]) -> pd.DataFrame:
        """Convert health entries to pandas DataFrame"""
        if not entries:
            return pd.DataFrame()
        
        df = pd.DataFrame(entries)
        # Convert MongoDB ObjectId values to strings for Arrow compatibility
        for col in df.columns:
            if df[col].dtype == 'object':
                df[col] = df[col].apply(lambda v: str(v) if isinstance(v, ObjectId) else v)
        df['date'] = pd.to_datetime(df['date'])
        return df
    
    @staticmethod
    def get_greeting() -> str:
        """Get time-appropriate greeting"""
        hour = datetime.now().hour
        
        if 5 <= hour < 12:
            return "Good Morning"
        elif 12 <= hour < 17:
            return "Good Afternoon"
        elif 17 <= hour < 21:
            return "Good Evening"
        else:
            return "Good Night"
