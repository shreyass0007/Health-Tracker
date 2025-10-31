"""
Data Models
Defines the structure of data objects
"""

from datetime import datetime
from typing import Optional
from dataclasses import dataclass, asdict

@dataclass
class User:
    """User model"""
    username: str
    email: str
    phone: str
    password_hash: str
    created_at: datetime = None
    updated_at: datetime = None
    
    def to_dict(self):
        return asdict(self)

@dataclass
class HealthEntry:
    """Health entry model"""
    user_id: str
    date: datetime
    steps: int
    calories: int
    heart_rate: int
    sleep_hours: float
    water_intake: int
    notes: Optional[str] = ""
    created_at: datetime = None
    
    def to_dict(self):
        return asdict(self)

@dataclass
class Streak:
    """Login streak model"""
    user_id: str
    current_streak: int
    longest_streak: int
    last_login: datetime
    login_dates: list
    updated_at: datetime = None
    
    def to_dict(self):
        return asdict(self)

@dataclass
class HealthTip:
    """AI health tip model"""
    user_id: str
    tip_text: str
    category: str
    created_at: datetime = None
    
    def to_dict(self):
        return asdict(self)
