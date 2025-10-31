"""
Input Validators
Validates user inputs and data
"""

import re
from typing import Any

class Validators:
    """Validation utilities"""
    
    @staticmethod
    def is_valid_email(email: str) -> bool:
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    @staticmethod
    def is_valid_phone(phone: str) -> bool:
        """Validate phone number format (international)"""
        # Remove spaces and dashes
        phone_clean = phone.replace(' ', '').replace('-', '')
        # Must start with + and have 10-15 digits
        pattern = r'^\+\d{10,15}$'
        return bool(re.match(pattern, phone_clean))
    
    @staticmethod
    def is_valid_password(password: str) -> bool:
        """Validate password strength"""
        return len(password) >= 6
    
    @staticmethod
    def is_valid_health_value(value: Any, min_val: float, max_val: float) -> bool:
        """Validate health metric value"""
        try:
            val = float(value)
            return min_val <= val <= max_val
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def validate_health_entry(entry: dict) -> tuple:
        """Validate complete health entry"""
        errors = []
        
        if not Validators.is_valid_health_value(entry.get('steps', 0), 0, 100000):
            errors.append("Steps must be between 0 and 100,000")
        
        if not Validators.is_valid_health_value(entry.get('calories', 0), 0, 10000):
            errors.append("Calories must be between 0 and 10,000")
        
        if not Validators.is_valid_health_value(entry.get('heart_rate', 0), 30, 220):
            errors.append("Heart rate must be between 30 and 220 bpm")
        
        if not Validators.is_valid_health_value(entry.get('sleep_hours', 0), 0, 24):
            errors.append("Sleep hours must be between 0 and 24")
        
        if not Validators.is_valid_health_value(entry.get('water_intake', 0), 0, 50):
            errors.append("Water intake must be between 0 and 50 glasses")
        
        return len(errors) == 0, errors
