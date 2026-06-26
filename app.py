"""
Streamlit application for Ukrainian air raid alert analysis.

Main UI entry point providing interactive time-series analysis
and regional comparison of historical air raid patterns.
"""

from datetime import datetime, timedelta

import streamlit as st
import pandas as pd

from data_loader import load_alerts, get_available_oblasts
from analytics import (
    filter_by_date_range,
    filter_by_oblasts,
    get_summary_statistics,
    get_oblast_comparison,
    get_monthly_distribution,
    get_weekday_distribution,
    get_hourly_distribution,
    get_notable_events,
    generate_analytical_summary,
)
from visualization import (
    create_monthly_trend_chart,
    create_weekday_distribution_chart,
    create_hourly_distribution_chart,
    create_oblast_comparison_chart,
)

# Page configuration
st.set_page_config(
    page_title="Ukrainian Air Raid Alert Analysis",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("🚨 Ukrainian Air Raid Alert Analysis")
st.markdown(
    "Historical time-series analysis of air raid patterns by region. "
    "Data provided by [sirens.in.ua](https://sirens.in.ua)"
)

# ============================================================================
# SIDEBAR: Data & Filters
# ============================================================================

with st.sidebar:
    st.header("⚙️ Settings")
    
    # Data refresh button
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.session_state.force_refresh = True
    
    st.divider()
    
    # Load data
    if "force_refresh" in st.session_state and st.session_state.force_refresh:
        df, status = load_alerts(force_refresh=True)
        st.session_state.force_refresh = False
    else:
        df, status = load_alerts(force_refresh=False)
    
    st.info(status)
    
    if df.empty:
        st.error("⚠️ Unable to load data. Please check your internet connection or try again later.")
        st.stop()
    
    st.divider()
    
    # Region selection
    st.subheader("📍 Regions")
    available_oblasts = get_available_oblasts(df)
    
    selected_oblasts = st.multiselect(
        "Select oblasts to analyze:",
        options=available_oblasts,
        default=available_oblasts[:3] if len(available_oblasts) >= 3 else available_oblasts,
        help="Choose one or more regions for comparison"
    )
    
    if not selected_oblasts:
        st.warning("Please select at least one region.")
        st.stop()
    
    st.divider()
    
    # Time period selection
    st.subheader("📅 Time Period")
    time_period = st.radio(
        "Select time range:",
        options=["Last Month", "Last Year", "Custom Range"],
        index=1
    )
    
    if time_period == "Last Month":
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
    elif time_period == "Last Year":
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
    else:  # Custom Range
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("From:", value=datetime.now() - timedelta(days=90))
        with col2:
            end_date = st.date_input("To:", value=datetime.now())

# ============================================================================
# MAIN CONTENT: Analysis
# ============================================================================

# Filter data
df_filtered = filter_by_oblasts(df, selected_oblasts)
df_filtered = filter_by_date_range(
    df_filtered,
    start_date=datetime.combine(start_date, datetime.min.time()),
    end_date=datetime.combine(end_date, datetime.max.time())
)

if df_filtered.empty:
    st.warning(f"No data found for selected regions and time period.")
    st.stop()

# Statistics
stats = get_summary_statistics(df_filtered)

# Display summary metrics
st.header("📈 Summary Metrics")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Total Alerts", stats["total_alerts"])
with col2:
    st.metric("Avg Duration", f"{stats['avg_duration_minutes']} min")
with col3:
    st.metric("Total Duration", f"{stats['total_duration_hours']} h")
with col4:
    st.metric("Longest Alert", f"{stats['longest_alert_minutes']} min")
with col5:
    st.metric("Regions", stats["unique_oblasts"])

st.divider()

# ============================================================================
# SECTION: Regional Comparison
# ============================================================================

st.header("🗺️ Regional Comparison")

comparison_df = get_oblast_comparison(df_filtered, selected_oblasts)

if not comparison_df.empty:
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Comparison Table")
        st.dataframe(
            comparison_df,
            use_container_width=True,
            hide_index=True
        )
    
    with col2:
        st.subheader("Alert Count by Oblast")
        fig = create_oblast_comparison_chart(comparison_df)
        st.pyplot(fig)
else:
    st.info("No data available for comparison.")

st.divider()

# ============================================================================
# SECTION: Time-Series Analysis
# ============================================================================

st.header("📊 Time-Series Analysis")

# Monthly trend
monthly_data = get_monthly_distribution(df_filtered)
st.subheader("Monthly Trend")
if not monthly_data.empty:
    fig = create_monthly_trend_chart(monthly_data)
    st.pyplot(fig)
else:
    st.info("Insufficient data for monthly trend.")

st.divider()

# Weekday & Hourly distributions
col1, col2 = st.columns(2)

with col1:
    st.subheader("Distribution by Day of Week")
    weekday_data = get_weekday_distribution(df_filtered)
    if not weekday_data.empty:
        fig = create_weekday_distribution_chart(weekday_data)
        st.pyplot(fig)
    else:
        st.info("No data available.")

with col2:
    st.subheader("Distribution by Hour of Day")
    hourly_data = get_hourly_distribution(df_filtered)
    if not hourly_data.empty:
        fig = create_hourly_distribution_chart(hourly_data)
        st.pyplot(fig)
    else:
        st.info("No data available.")

st.divider()

# ============================================================================
# SECTION: Notable Events
# ============================================================================

st.header("⭐ Notable Historical Events")

notable = get_notable_events(df_filtered)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Longest Alert", notable["longest_alert"].split(":")[1].strip() if ":" in notable["longest_alert"] else notable["longest_alert"])

with col2:
    st.metric("Day with Most Alerts", notable["day_highest_alerts"].split(":")[1].strip() if ":" in notable["day_highest_alerts"] else notable["day_highest_alerts"])

with col3:
    st.metric("Month with Most Activity", notable["month_highest_activity"].split(":")[1].strip() if ":" in notable["month_highest_activity"] else notable["month_highest_activity"])

st.divider()

# ============================================================================
# SECTION: Analytical Summary
# ============================================================================

st.header("📝 Analytical Summary")

summary_text = generate_analytical_summary(df_filtered, selected_oblasts, stats)
st.markdown(summary_text)

st.divider()

# ============================================================================
# FOOTER
# ============================================================================

st.markdown(
    """
    ---
    
    **About This Application**
    
    This application provides historical analysis of Ukrainian air raid alerts.
    It focuses on **past patterns only** and does not forecast future events.
    
    Data source: [sirens.in.ua](https://sirens.in.ua) API  
    Last updated: Check 'Settings' → 'Refresh Data' status  
    
    *For emergencies, refer to official Ukrainian civil defense sources.*
    """
)
