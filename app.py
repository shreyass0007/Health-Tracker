"""
Health Tracker Pro - Main Application
A comprehensive health tracking system with AI-powered insights
"""

import streamlit as st
from datetime import datetime
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent))

from auth_service import AuthService
from streak_service import StreakService
from config import Config

# Page configuration
st.set_page_config(
    page_title="Health Tracker Pro",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for improved light UI
st.markdown("""
    <style>
    :root {
        --primary: #1f77b4;
        --bg: #FFFFFF;
        --bg-soft: #F7F9FC;
        --text: #0f172a;
        --muted: #64748b;
        --card: #FFFFFF;
        --shadow: 0 4px 12px rgba(15, 23, 42, 0.06);
        --radius: 12px;
    }

    /* Page base */
    .main-header {
        font-size: 2.25rem;
        line-height: 1.2;
        font-weight: 800;
        color: var(--primary);
        text-align: center;
        margin: 0 0 1.25rem 0;
    }
    .sub-header {
        color: var(--muted);
        text-align: center;
        margin-bottom: 1.75rem;
    }

    /* Cards */
    .metric-card, .info-card {
        background: var(--card);
        padding: 1.25rem 1.25rem;
        border-radius: var(--radius);
        box-shadow: var(--shadow);
        border: 1px solid #eef2f7;
    }

    /* Buttons */
    .stButton>button {
        width: 100%;
        background: var(--primary) !important;
        color: #fff !important;
        border-radius: 10px !important;
        padding: 0.6rem 1rem !important;
        border: none !important;
        font-weight: 700 !important;
        letter-spacing: .2px;
        transition: transform .04s ease, filter .15s ease;
    }
    .stButton>button:hover { filter: brightness(0.95); }
    .stButton>button:active { transform: translateY(1px); }

    /* Messages */
    .success-message, .error-message {
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .success-message { background: #e8f7ef; color: #17633b; border: 1px solid #c9efd9; }
    .error-message { background: #fdecec; color: #991b1b; border: 1px solid #ffd7d7; }

    /* Sidebar tweaks */
    section[data-testid="stSidebar"] .block-container {
        padding-top: 1rem;
    }

    /* Inputs */
    .stTextInput>div>div>input,
    .stNumberInput>div>div>input,
    .stTextArea textarea {
        border-radius: 10px !important;
        border: 1px solid #e5e7eb !important;
    }

    /* Divider */
    .hr-soft { border: none; border-top: 1px solid #eef2f7; margin: 1rem 0 1.25rem; }

    /* Footer */
    .app-footer { color: var(--muted); text-align: center; font-size: .9rem; margin-top: 1.25rem; }
    </style>
""", unsafe_allow_html=True)

# Initialize services
@st.cache_resource
def init_services():
    """Initialize all services with caching"""
    auth_service = AuthService()
    streak_service = StreakService()
    return auth_service, streak_service

auth_service, streak_service = init_services()

# Initialize session state
def init_session_state():
    """Initialize session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'email' not in st.session_state:
        st.session_state.email = None
    if 'page' not in st.session_state:
        st.session_state.page = 'dashboard'

init_session_state()

def login_page():
    """Render login/signup page"""
    st.markdown('<div class="main-header">🩺 Health Tracker Pro</div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        tab1, tab2 = st.tabs(["🔐 Login", "📝 Sign Up"])
        
        with tab1:
            st.subheader("Welcome Back!")
            with st.form("login_form"):
                email = st.text_input("📧 Email", placeholder="your.email@example.com")
                password = st.text_input("🔒 Password", type="password")
                submit = st.form_submit_button("Login", use_container_width=True)
                
                if submit:
                    if email and password:
                        user = auth_service.login(email, password)
                        if user:
                            st.session_state.authenticated = True
                            st.session_state.user_id = user['_id']
                            st.session_state.username = user['username']
                            st.session_state.email = user['email']
                            
                            # Track login streak
                            streak_service.record_login(str(user['_id']))
                            
                            st.success("✅ Login successful!")
                            st.rerun()
                        else:
                            st.error("❌ Invalid email or password")
                    else:
                        st.warning("⚠️ Please fill in all fields")
        
        with tab2:
            st.subheader("Create Your Account")
            with st.form("signup_form"):
                username = st.text_input("👤 Username", placeholder="johndoe")
                email = st.text_input("📧 Email", placeholder="your.email@example.com")
                phone = st.text_input("📱 Phone (with country code)", placeholder="+1234567890")
                password = st.text_input("🔒 Password", type="password")
                password_confirm = st.text_input("🔒 Confirm Password", type="password")
                
                submit = st.form_submit_button("Sign Up", use_container_width=True)
                
                if submit:
                    if username and email and phone and password and password_confirm:
                        if password != password_confirm:
                            st.error("❌ Passwords don't match!")
                        elif len(password) < 6:
                            st.error("❌ Password must be at least 6 characters")
                        else:
                            result = auth_service.signup(username, email, phone, password)
                            if result['success']:
                                st.success("✅ Account created successfully! Please login.")
                            else:
                                st.error(f"❌ {result['message']}")
                    else:
                        st.warning("⚠️ Please fill in all fields")

def main_app():
    """Render main application after authentication"""
    import dashboard, add_entry, analytics, tips, profile
    
    # Sidebar navigation
    with st.sidebar:
        st.markdown(f"### 👤 Welcome, {st.session_state.username}!")
        
        # Display login streak
        streak_data = streak_service.get_streak(st.session_state.user_id)
        if streak_data:
            st.markdown(f"""
            <div class="metric-card">
                <h3 style="text-align: center;">🔥 {streak_data['current_streak']} Day Streak!</h3>
                <p style="text-align: center; color: gray;">Keep it up!</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Navigation buttons
        if st.button("📊 Dashboard", use_container_width=True):
            st.session_state.page = 'dashboard'
        if st.button("➕ Add Health Data", use_container_width=True):
            st.session_state.page = 'add_entry'
        if st.button("📈 Analytics", use_container_width=True):
            st.session_state.page = 'analytics'
        if st.button("💡 AI Health Tips", use_container_width=True):
            st.session_state.page = 'tips'
        if st.button("👤 Profile", use_container_width=True):
            st.session_state.page = 'profile'
        
        st.markdown("---")
        
        if st.button("🚪 Logout", use_container_width=True):
            # Clear session state
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()

    # Render selected page
    if st.session_state.page == 'dashboard':
        dashboard.render(st.session_state.user_id)
    elif st.session_state.page == 'add_entry':
        add_entry.render(st.session_state.user_id)
    elif st.session_state.page == 'analytics':
        analytics.render(st.session_state.user_id)
    elif st.session_state.page == 'tips':
        tips.render(st.session_state.user_id)
    elif st.session_state.page == 'profile':
        profile.render(st.session_state.user_id, st.session_state.username, st.session_state.email)

    # Footer
    st.markdown('<hr class="hr-soft" />', unsafe_allow_html=True)
    st.markdown('<div class="app-footer">Made with 🩺 Health Tracker Pro</div>', unsafe_allow_html=True)

def main():
    """Main application entry point"""
    if not st.session_state.get('authenticated', False):
        login_page()
    else:
        main_app()

if __name__ == "__main__":
    main()
