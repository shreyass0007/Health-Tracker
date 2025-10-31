"""
MongoDB Database Manager
Handles all database operations with connection pooling
"""

from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure, DuplicateKeyError
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import streamlit as st
from config import Config

class DatabaseManager:
    """Singleton database manager for MongoDB operations"""
    
    _instance = None
    _client = None
    _db = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize database connection"""
        if self._client is None:
            try:
                self._client = MongoClient(
                    Config.MONGODB_URI,
                    serverSelectionTimeoutMS=5000,
                    maxPoolSize=50
                )
                # Test connection
                self._client.admin.command('ping')
                self._db = self._client[Config.MONGODB_DB_NAME]
                self._setup_indexes()
                print("✅ MongoDB connected successfully")
            except ConnectionFailure as e:
                print(f"❌ MongoDB connection failed: {e}")
                raise
    
    def _setup_indexes(self):
        """Create database indexes for better performance"""
        # Users collection indexes
        self._db.users.create_index([("email", ASCENDING)], unique=True)
        self._db.users.create_index([("username", ASCENDING)], unique=True)
        
        # Health entries collection indexes
        self._db.health_entries.create_index([("user_id", ASCENDING), ("date", DESCENDING)])
        self._db.health_entries.create_index([("user_id", ASCENDING)])
        
        # Streaks collection indexes
        self._db.streaks.create_index([("user_id", ASCENDING)], unique=True)
        
        # Tips collection indexes
        self._db.tips.create_index([("user_id", ASCENDING), ("created_at", DESCENDING)])
    
    # ============= USER OPERATIONS =============
    
    def create_user(self, user_data: Dict) -> Optional[str]:
        """Create a new user"""
        try:
            user_data['created_at'] = datetime.utcnow()
            user_data['updated_at'] = datetime.utcnow()
            result = self._db.users.insert_one(user_data)
            return str(result.inserted_id)
        except DuplicateKeyError:
            return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        return self._db.users.find_one({"email": email})
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """Get user by ID"""
        from bson import ObjectId
        return self._db.users.find_one({"_id": ObjectId(user_id)})
    
    def update_user(self, user_id: str, update_data: Dict) -> bool:
        """Update user information"""
        from bson import ObjectId
        update_data['updated_at'] = datetime.utcnow()
        result = self._db.users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )
        return result.modified_count > 0
    
    # ============= HEALTH ENTRY OPERATIONS =============
    
    def create_health_entry(self, entry_data: Dict) -> Optional[str]:
        """Create a new health entry"""
        entry_data['created_at'] = datetime.utcnow()
        result = self._db.health_entries.insert_one(entry_data)
        return str(result.inserted_id)
    
    def get_health_entries(self, user_id: str, days: int = 30) -> List[Dict]:
        """Get health entries for a user for the last N days"""
        from bson import ObjectId
        start_date = datetime.utcnow() - timedelta(days=days)
        
        entries = list(self._db.health_entries.find({
            "user_id": ObjectId(user_id),
            "date": {"$gte": start_date}
        }).sort("date", DESCENDING))
        
        return entries
    
    def get_entry_by_date(self, user_id: str, date: datetime) -> Optional[Dict]:
        """Get health entry for a specific date"""
        from bson import ObjectId
        # Create date range for the entire day
        start_of_day = datetime(date.year, date.month, date.day)
        end_of_day = start_of_day + timedelta(days=1)
        
        return self._db.health_entries.find_one({
            "user_id": ObjectId(user_id),
            "date": {"$gte": start_of_day, "$lt": end_of_day}
        })
    
    def update_health_entry(self, entry_id: str, update_data: Dict) -> bool:
        """Update a health entry"""
        from bson import ObjectId
        result = self._db.health_entries.update_one(
            {"_id": ObjectId(entry_id)},
            {"$set": update_data}
        )
        return result.modified_count > 0
    
    def get_health_stats(self, user_id: str, days: int = 30) -> Dict:
        """Get aggregated health statistics"""
        from bson import ObjectId
        start_date = datetime.utcnow() - timedelta(days=days)
        
        pipeline = [
            {
                "$match": {
                    "user_id": ObjectId(user_id),
                    "date": {"$gte": start_date}
                }
            },
            {
                "$group": {
                    "_id": None,
                    "avg_steps": {"$avg": "$steps"},
                    "avg_calories": {"$avg": "$calories"},
                    "avg_heart_rate": {"$avg": "$heart_rate"},
                    "avg_sleep": {"$avg": "$sleep_hours"},
                    "avg_water": {"$avg": "$water_intake"},
                    "total_entries": {"$sum": 1}
                }
            }
        ]
        
        result = list(self._db.health_entries.aggregate(pipeline))
        return result[0] if result else {}
    
    # ============= STREAK OPERATIONS =============
    
    def upsert_streak(self, user_id: str, streak_data: Dict) -> bool:
        """Create or update user streak"""
        from bson import ObjectId
        # Do not overwrite the unique user_id field during updates to avoid duplicate key errors
        # Ensure user_id is consistently stored as an ObjectId and only set on insert
        update_data = {k: v for k, v in streak_data.items() if k != 'user_id'}
        update_data['updated_at'] = datetime.utcnow()

        result = self._db.streaks.update_one(
            {"user_id": ObjectId(user_id)},
            {
                "$set": update_data,
                "$setOnInsert": {"user_id": ObjectId(user_id)}
            },
            upsert=True
        )
        return result.acknowledged
    
    def get_streak(self, user_id: str) -> Optional[Dict]:
        """Get user streak data"""
        from bson import ObjectId
        return self._db.streaks.find_one({"user_id": ObjectId(user_id)})
    
    # ============= TIPS OPERATIONS =============
    
    def save_tip(self, tip_data: Dict) -> Optional[str]:
        """Save an AI-generated tip"""
        tip_data['created_at'] = datetime.utcnow()
        result = self._db.tips.insert_one(tip_data)
        return str(result.inserted_id)
    
    def get_recent_tips(self, user_id: str, limit: int = 10) -> List[Dict]:
        """Get recent tips for a user"""
        from bson import ObjectId
        tips = list(self._db.tips.find({
            "user_id": ObjectId(user_id)
        }).sort("created_at", DESCENDING).limit(limit))
        return tips
    
    def get_tip_for_today(self, user_id: str) -> Optional[Dict]:
        """Get tip generated today"""
        from bson import ObjectId
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        return self._db.tips.find_one({
            "user_id": ObjectId(user_id),
            "created_at": {"$gte": today_start}
        })
    
    # ============= ADMIN OPERATIONS =============
    
    def get_all_users_count(self) -> int:
        """Get total number of users"""
        return self._db.users.count_documents({})
    
    def get_total_entries_count(self) -> int:
        """Get total number of health entries"""
        return self._db.health_entries.count_documents({})
    
    def close_connection(self):
        """Close database connection"""
        if self._client:
            self._client.close()
            print("MongoDB connection closed")
