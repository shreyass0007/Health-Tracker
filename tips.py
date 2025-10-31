"""
Tips Page
Displays AI-generated health tips
"""

import streamlit as st
from openai_service import OpenAIService

def render(user_id):
    st.markdown('<div class="main-header">💡 Your AI Health Tips</div>', unsafe_allow_html=True)
    ai_service = OpenAIService()
    tips = ai_service.db.get_recent_tips(user_id, limit=10)

    if not tips:
        st.info("No tips generated yet. Log your health data to get personalized AI tips!")
        return

    for t in tips:
        cat = t.get('category', 'general')
        emoji = ai_service.get_category_emoji(cat)
        st.markdown(f"> {emoji} **{t['tip_text']}**  \n<sub>[{t['created_at'].strftime('%Y-%m-%d')}]</sub>")
