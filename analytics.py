"""
Analytics Page
Visualizes trends and progress with charts
"""

import streamlit as st
from health_service import HealthService
import altair as alt
from helpers import Helpers

def render(user_id):
    st.markdown('<div class="main-header">📈 Analytics & Trends</div>', unsafe_allow_html=True)
    health_service = HealthService()

    # Fetch health data for last 30 days
    entries = health_service.get_entries(user_id, days=30)
    df = Helpers.entries_to_dataframe(entries)

    if df.empty:
        st.info("No health entries yet. Add your data to see charts.")
        return

    st.subheader("Weekly Trends")
    week_df = df.tail(7)
    for metric in ["steps", "calories", "sleep_hours", "water_intake", "heart_rate"]:
        chart = alt.Chart(week_df).mark_line(point=True).encode(
            x=alt.X('date:T', title='Date'),
            y=alt.Y(f"{metric}:Q", title=metric.replace('_', ' ').title()),
            tooltip=['date', metric]
        ).properties(width=500, height=200)
        st.altair_chart(chart, width='stretch')

    # Show 30-day progression
    st.subheader("30-Day Overview")
    metrics = ['steps', 'calories', 'heart_rate', 'sleep_hours', 'water_intake']
    st.dataframe(df[["date"] + metrics].sort_values('date', ascending=False), width='stretch')
