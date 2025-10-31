"""
Add Entry Page
Form to input today’s health metrics
"""

import streamlit as st
from datetime import datetime
from health_service import HealthService
from validators import Validators

def render(user_id):
    st.markdown('<div class="main-header">➕ Add Today\'s Health Data</div>', unsafe_allow_html=True)
    health_service = HealthService()

    with st.form("add_data"):
        today = datetime.utcnow()
        steps = st.number_input("🚶 Steps", min_value=0, step=100, value=0)
        calories = st.number_input("🔥 Calories", min_value=0, max_value=10000, step=25, value=0)
        heart_rate = st.number_input("💓 Heart Rate (bpm)", min_value=30, max_value=220, step=1, value=60)
        sleep_hours = st.number_input("😴 Sleep (hours)", min_value=0.0, max_value=24.0, step=0.1, value=0.0)
        water_intake = st.number_input("💧 Water (glasses)", min_value=0, max_value=50, step=1, value=0)
        notes = st.text_area("📝 Notes (optional)", max_chars=320)
        submit = st.form_submit_button("Save Entry")

    if submit:
        entry = dict(
            date=today,
            steps=int(steps),
            calories=int(calories),
            heart_rate=int(heart_rate),
            sleep_hours=float(sleep_hours),
            water_intake=int(water_intake),
            notes=notes
        )
        is_valid, errs = Validators.validate_health_entry(entry)
        if not is_valid:
            st.error("Errors: " + "; ".join(errs))
        else:
            result = health_service.add_entry(user_id, entry)
            if result["success"]:
                st.success(result["message"])
            else:
                st.error(result["message"])
