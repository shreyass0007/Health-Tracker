"""
Authentication Service
Handles user authentication and authorization
"""

import bcrypt
from typing import Optional, Dict
from db_manager import DatabaseManager
from models import User
from validators import Validators

class AuthService:
    """Authentication service for user management"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.validators = Validators()
    
    def _hash_password(self, password: str) -> str:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def _verify_password(self, password: str, hashed: str) -> bool:
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    
    def signup(self, username: str, email: str, phone: str, password: str) -> Dict:
        """Register a new user"""
        # Validate inputs
        if not self.validators.is_valid_email(email):
            return {"success": False, "message": "Invalid email format"}
        
        if not self.validators.is_valid_phone(phone):
            return {"success": False, "message": "Invalid phone format (use +1234567890)"}
        
        if not self.validators.is_valid_password(password):
            return {"success": False, "message": "Password must be at least 6 characters"}
        
        # Check if user already exists
        if self.db.get_user_by_email(email):
            return {"success": False, "message": "Email already registered"}
        
        # Create user
        user = User(
            username=username,
            email=email,
            phone=phone,
            password_hash=self._hash_password(password)
        )
        
        user_id = self.db.create_user(user.to_dict())
        
        if user_id:
            return {"success": True, "message": "Account created successfully", "user_id": user_id}
        else:
            return {"success": False, "message": "Failed to create account"}
    
    def login(self, email: str, password: str) -> Optional[Dict]:
        """Authenticate user"""
        user = self.db.get_user_by_email(email)
        
        if user and self._verify_password(password, user['password_hash']):
            # Remove password hash from returned user data
            user_data = {k: v for k, v in user.items() if k != 'password_hash'}
            return user_data
        
        return None
    
    def update_password(self, user_id: str, old_password: str, new_password: str) -> Dict:
        """Update user password"""
        user = self.db.get_user_by_id(user_id)
        
        if not user:
            return {"success": False, "message": "User not found"}
        
        if not self._verify_password(old_password, user['password_hash']):
            return {"success": False, "message": "Incorrect current password"}
        
        if not self.validators.is_valid_password(new_password):
            return {"success": False, "message": "New password must be at least 6 characters"}
        
        new_hash = self._hash_password(new_password)
        success = self.db.update_user(user_id, {"password_hash": new_hash})
        
        if success:
            return {"success": True, "message": "Password updated successfully"}
        else:
            return {"success": False, "message": "Failed to update password"}
