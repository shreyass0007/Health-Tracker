"""
Dashboard Page
Displays user's key health stats, progress, and streaks
"""

import streamlit as st
from health_service import HealthService
from openai_service import OpenAIService
from streak_service import StreakService
from helpers import Helpers

def render(user_id):
    health_service = HealthService()
    ai_service = OpenAIService()
    streak_service = StreakService()

    # Header
    st.markdown('<div class="main-header">📊 Your Health Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Your weekly snapshot, progress, and motivation in one place.</div>', unsafe_allow_html=True)

    # Weekly metrics
    stats = health_service.get_statistics(user_id, days=7)
    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 0.9rem; color:#64748b;">Avg Steps</div>
            <div style="font-size: 1.6rem; font-weight:800;">{stats.get('avg_steps', 0):,}</div>
        </div>
        """, unsafe_allow_html=True)
    with m2:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 0.9rem; color:#64748b;">Avg Calories</div>
            <div style="font-size: 1.6rem; font-weight:800;">{stats.get('avg_calories', 0):,}</div>
        </div>
        """, unsafe_allow_html=True)
    with m3:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 0.9rem; color:#64748b;">Avg Sleep</div>
            <div style="font-size: 1.6rem; font-weight:800;">{stats.get('avg_sleep', 0)} h</div>
        </div>
        """, unsafe_allow_html=True)
    with m4:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 0.9rem; color:#64748b;">Avg Water</div>
            <div style="font-size: 1.6rem; font-weight:800;">{stats.get('avg_water', 0)} glasses</div>
        </div>
        """, unsafe_allow_html=True)
    with m5:
        st.markdown(f"""
        <div class="metric-card">
            <div style="font-size: 0.9rem; color:#64748b;">Avg HR</div>
            <div style="font-size: 1.6rem; font-weight:800;">{stats.get('avg_heart_rate', 0)} bpm</div>
        </div>
        """, unsafe_allow_html=True)

    # Today's score and streak
    c1, c2 = st.columns([1.2, 1])
    with c1:
        today_entry = health_service.get_today_entry(user_id)
        if today_entry:
            score = health_service.calculate_health_score(today_entry)
            status, icon, txt = Helpers.get_health_status(score)
            st.markdown(f"""
            <div class="info-card">
                <div style="display:flex; align-items:center; gap:.5rem;">
                    <div style="font-weight:800; font-size:1.1rem;">Today’s Health Score</div>
                    <span style="background:#eef2f7; color:#0f172a; padding:.15rem .5rem; border-radius:999px; font-size:.85rem;">{status} {icon}</span>
                </div>
                <div style="font-size:2rem; font-weight:800; margin:.25rem 0 .25rem;">{score}/100</div>
                <div style="color:#64748b;">{txt}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("<div class='info-card'>No entry for today yet. Add your health data to see your score.</div>", unsafe_allow_html=True)

    with c2:
        streak = streak_service.get_streak(user_id)
        if streak:
            st.markdown(f"""
            <div class="info-card" style="text-align:center;">
                <div style="font-size:.95rem; color:#64748b;">Login Streak</div>
                <div style="font-size:2rem; font-weight:800;">🔥 {streak['current_streak']} days</div>
                <div style="color:#64748b;">Longest: {streak['longest_streak']} days</div>
            </div>
            """, unsafe_allow_html=True)

    # AI tip of the day
    ai_tip = ai_service.generate_health_tip(user_id, stats)
    if ai_tip["success"]:
        tip_category = ai_tip.get("category", "general")
        tip_emoji = ai_service.get_category_emoji(tip_category)
        st.markdown(f"""
        <div class="info-card" style="margin-top:1rem;">
            <div style="font-weight:800; margin-bottom:.25rem;">{tip_emoji} Health Tip</div>
            <div style="color:#0f172a; line-height:1.6;">{ai_tip['tip']}</div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("<div class='info-card' style='margin-top:1rem;'>Health tips are unavailable at the moment.</div>", unsafe_allow_html=True)
