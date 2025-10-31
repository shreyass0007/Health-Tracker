"""
Configuration Management
Handles environment variables and application settings
"""

import os
from dotenv import load_dotenv

# Load environment variables (override any existing system env to avoid stale values)
load_dotenv(override=True)

class Config:
    """Application configuration"""
    
    # MongoDB Configuration
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/')
    MONGODB_DB_NAME = os.getenv('MONGODB_DB_NAME', 'health_tracker_db')
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
    
    # Twilio Configuration
    TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', '')
    TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', '')
    TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER', '')
    
    # Pixela Configuration
    PIXELA_USERNAME = os.getenv('PIXELA_USERNAME', '')
    PIXELA_TOKEN = os.getenv('PIXELA_TOKEN', '')
    
    # Application Settings
    APP_NAME = "Health Tracker Pro"
    APP_VERSION = "1.0.0"
    
    # Health Metrics Defaults
    DEFAULT_STEP_GOAL = 10000
    DEFAULT_WATER_GOAL = 8  # glasses
    DEFAULT_SLEEP_GOAL = 8  # hours
    DEFAULT_CALORIE_GOAL = 2000
    
    # Session Configuration
    SESSION_COOKIE_NAME = "health_tracker_session"
    SESSION_EXPIRY_DAYS = 30
    
    @classmethod
    def validate_config(cls):
        """Validate required configuration"""
        errors = []
        
        if not cls.MONGODB_URI:
            errors.append("MONGODB_URI is not set")
        if not cls.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY is not set (AI tips will be disabled)")
        if not cls.TWILIO_ACCOUNT_SID or not cls.TWILIO_AUTH_TOKEN:
            errors.append("Twilio credentials not set (SMS features will be disabled)")
        
        return errors
    
    @classmethod
    def is_feature_enabled(cls, feature):
        """Check if a feature is enabled based on configuration"""
        feature_flags = {
            'ai_tips': bool(cls.OPENAI_API_KEY),
            'sms_notifications': bool(cls.TWILIO_ACCOUNT_SID and cls.TWILIO_AUTH_TOKEN),
            'pixela_tracking': bool(cls.PIXELA_USERNAME and cls.PIXELA_TOKEN)
        }
        return feature_flags.get(feature, False)
