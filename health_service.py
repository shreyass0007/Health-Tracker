"""
Health Service
Manages health data operations and analytics
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from db_manager import DatabaseManager
from models import HealthEntry
from bson import ObjectId

class HealthService:
    """Service for managing health data"""
    
    def __init__(self):
        self.db = DatabaseManager()
    
    def add_entry(self, user_id: str, entry_data: Dict) -> Dict:
        """Add a new health entry"""
        # Check if entry for today already exists
        existing_entry = self.db.get_entry_by_date(user_id, entry_data['date'])
        
        if existing_entry:
            # Update existing entry
            success = self.db.update_health_entry(str(existing_entry['_id']), entry_data)
            return {
                "success": success,
                "message": "Entry updated successfully" if success else "Failed to update entry"
            }
        else:
            # Create new entry
            entry = HealthEntry(
                user_id=ObjectId(user_id),
                date=entry_data['date'],
                steps=entry_data['steps'],
                calories=entry_data['calories'],
                heart_rate=entry_data['heart_rate'],
                sleep_hours=entry_data['sleep_hours'],
                water_intake=entry_data['water_intake'],
                notes=entry_data.get('notes', '')
            )
            
            entry_id = self.db.create_health_entry(entry.to_dict())
            
            if entry_id:
                return {"success": True, "message": "Entry added successfully"}
            else:
                return {"success": False, "message": "Failed to add entry"}
    
    def get_entries(self, user_id: str, days: int = 30) -> List[Dict]:
        """Get health entries for a user"""
        return self.db.get_health_entries(user_id, days)
    
    def get_today_entry(self, user_id: str) -> Optional[Dict]:
        """Get today's health entry"""
        return self.db.get_entry_by_date(user_id, datetime.utcnow())
    
    def get_statistics(self, user_id: str, days: int = 30) -> Dict:
        """Get health statistics"""
        stats = self.db.get_health_stats(user_id, days)
        
        # Format and round values
        formatted_stats = {}
        if stats:
            formatted_stats = {
                'avg_steps': round(stats.get('avg_steps', 0)),
                'avg_calories': round(stats.get('avg_calories', 0)),
                'avg_heart_rate': round(stats.get('avg_heart_rate', 0)),
                'avg_sleep': round(stats.get('avg_sleep', 0), 1),
                'avg_water': round(stats.get('avg_water', 0), 1),
                'total_entries': stats.get('total_entries', 0)
            }
        
        return formatted_stats
    
    def get_weekly_trends(self, user_id: str) -> Dict:
        """Get weekly trend data for charts"""
        entries = self.get_entries(user_id, days=7)
        
        # Sort by date
        entries.sort(key=lambda x: x['date'])
        
        trends = {
            'dates': [],
            'steps': [],
            'calories': [],
            'sleep': [],
            'water': [],
            'heart_rate': []
        }
        
        for entry in entries:
            trends['dates'].append(entry['date'].strftime('%Y-%m-%d'))
            trends['steps'].append(entry['steps'])
            trends['calories'].append(entry['calories'])
            trends['sleep'].append(entry['sleep_hours'])
            trends['water'].append(entry['water_intake'])
            trends['heart_rate'].append(entry['heart_rate'])
        
        return trends
    
    def calculate_health_score(self, entry: Dict) -> int:
        """Calculate a health score based on daily metrics (0-100)"""
        score = 0
        
        # Steps (max 30 points)
        if entry['steps'] >= 10000:
            score += 30
        else:
            score += (entry['steps'] / 10000) * 30
        
        # Sleep (max 25 points)
        if 7 <= entry['sleep_hours'] <= 9:
            score += 25
        elif entry['sleep_hours'] < 7:
            score += (entry['sleep_hours'] / 7) * 25
        else:
            score += 15
        
        # Water (max 20 points)
        if entry['water_intake'] >= 8:
            score += 20
        else:
            score += (entry['water_intake'] / 8) * 20
        
        # Heart rate (max 15 points)
        if 60 <= entry['heart_rate'] <= 100:
            score += 15
        elif entry['heart_rate'] < 60:
            score += 10
        else:
            score += 5
        
        # Calories (max 10 points) - within reasonable range
        if 1500 <= entry['calories'] <= 2500:
            score += 10
        else:
            score += 5
        
        return min(round(score), 100)
