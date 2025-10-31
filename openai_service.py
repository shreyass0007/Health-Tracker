"""
OpenAI Service
Generates personalized health tips using ChatGPT
"""

from openai import OpenAI
from typing import Dict, Optional
from config import Config
from db_manager import DatabaseManager

class OpenAIService:
    """Service for AI-powered health tips"""
    
    def __init__(self):
        self.client = None
        self.db = DatabaseManager()
        
        if Config.OPENAI_API_KEY:
            self.client = OpenAI(api_key=Config.OPENAI_API_KEY)
        else:
            print("⚠️ OpenAI API key not configured. AI tips disabled.")
    
    def generate_health_tip(self, user_id: str, health_data: Optional[Dict] = None) -> Dict:
        """Generate a personalized health tip"""
        if not self.client:
            return {
                "success": False,
                "message": "AI tips feature is not configured"
            }
        
        # Check if tip already generated today
        existing_tip = self.db.get_tip_for_today(user_id)
        if existing_tip:
            return {
                "success": True,
                "tip": existing_tip['tip_text'],
                "category": existing_tip.get('category', 'general'),
                "from_cache": True
            }
        
        # Generate prompt based on health data
        if health_data:
            prompt = self._create_personalized_prompt(health_data)
        else:
            prompt = "Give a short, motivational health tip (2-3 sentences) for someone trying to maintain a healthy lifestyle."
        
        try:
            response = self.client.chat.completions.create(
                model=Config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "You are a friendly health coach providing concise, actionable health tips."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=150,
                temperature=0.7
            )
            
            tip_text = response.choices[0].message.content.strip()
            category = self._categorize_tip(tip_text)
            
            # Save tip to database
            from bson import ObjectId
            tip_data = {
                "user_id": ObjectId(user_id),
                "tip_text": tip_text,
                "category": category
            }
            self.db.save_tip(tip_data)
            
            return {
                "success": True,
                "tip": tip_text,
                "category": category,
                "from_cache": False
            }
            
        except Exception as e:
            print(f"Error generating tip: {e}")
            return {
                "success": False,
                "message": f"Failed to generate tip: {str(e)}"
            }
    
    def _create_personalized_prompt(self, health_data: Dict) -> str:
        """Create a personalized prompt based on user's health data"""
        avg_steps = health_data.get('avg_steps', 0)
        avg_sleep = health_data.get('avg_sleep', 0)
        avg_water = health_data.get('avg_water', 0)
        
        prompt = f"""Based on the following health metrics, give a short motivational tip (2-3 sentences):
        - Average daily steps: {avg_steps}
        - Average sleep hours: {avg_sleep}
        - Average water intake: {avg_water} glasses
        
        Focus on the area that needs the most improvement and provide actionable advice."""
        
        return prompt
    
    def _categorize_tip(self, tip_text: str) -> str:
        """Categorize the tip based on its content"""
        tip_lower = tip_text.lower()
        
        if any(word in tip_lower for word in ['sleep', 'rest', 'bed']):
            return 'sleep'
        elif any(word in tip_lower for word in ['water', 'hydrat', 'drink']):
            return 'hydration'
        elif any(word in tip_lower for word in ['step', 'walk', 'exercise', 'active']):
            return 'activity'
        elif any(word in tip_lower for word in ['food', 'eat', 'nutrition', 'diet']):
            return 'nutrition'
        else:
            return 'general'
    
    def get_category_emoji(self, category: str) -> str:
        """Get emoji for tip category"""
        emoji_map = {
            'sleep': '😴',
            'hydration': '💧',
            'activity': '🏃',
            'nutrition': '🥗',
            'general': '💡'
        }
        return emoji_map.get(category, '💡')
