"""
Profile Page
User's profile and stats summary
"""

import streamlit as st
from auth_service import AuthService

def render(user_id, username, email):
    st.markdown('<div class="main-header">👤 My Profile</div>', unsafe_allow_html=True)
    st.write(f"**Username:** {username}")
    st.write(f"**Email:** {email}")

    # Profile update and password change can be implemented here
    st.markdown("---")
    st.info("🔒 For security, you can request a password change. More profile features coming soon!")
