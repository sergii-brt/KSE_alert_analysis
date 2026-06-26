"""
Chart generation and visualization helpers.

Creates matplotlib-based visualizations for time-series analysis.
"""

import matplotlib.pyplot as plt
import pandas as pd


def create_monthly_trend_chart(monthly_data: pd.DataFrame) -> plt.Figure:
    """Create line chart of alerts by month."""
    if monthly_data.empty:
        fig, ax = plt.subplots(figsize=(12, 5))
        ax.text(0.5, 0.5, "No data available", ha="center", va="center")
        return fig
    
    fig, ax = plt.subplots(figsize=(12, 5))
    
    ax.plot(
        monthly_data["month_str"],
        monthly_data["alert_count"],
        marker="o",
        linewidth=2,
        markersize=6,
        color="#ef4444"
    )
    
    ax.set_xlabel("Month", fontsize=11)
    ax.set_ylabel("Number of Alerts", fontsize=11)
    ax.set_title("Monthly Alert Trend", fontsize=13, fontweight="bold")
    ax.grid(True, alpha=0.3)
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    
    return fig


def create_weekday_distribution_chart(weekday_data: pd.DataFrame) -> plt.Figure:
    """Create bar chart of alerts by day of week."""
    if weekday_data.empty:
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.text(0.5, 0.5, "No data available", ha="center", va="center")
        return fig
    
    fig, ax = plt.subplots(figsize=(10, 5))
    
    colors = ["#3b82f6" if i < 5 else "#8b5cf6" for i in range(len(weekday_data))]
    
    ax.bar(
        weekday_data["Day of Week"],
        weekday_data["alert_count"],
        color=colors,
        edgecolor="black",
        linewidth=1.2
    )
    
    ax.set_xlabel("Day of Week", fontsize=11)
    ax.set_ylabel("Number of Alerts", fontsize=11)
    ax.set_title("Alert Distribution by Day of Week", fontsize=13, fontweight="bold")
    ax.grid(True, alpha=0.3, axis="y")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    
    return fig


def create_hourly_distribution_chart(hourly_data: pd.DataFrame) -> plt.Figure:
    """Create bar chart of alerts by hour of day."""
    if hourly_data.empty:
        fig, ax = plt.subplots(figsize=(12, 5))
        ax.text(0.5, 0.5, "No data available", ha="center", va="center")
        return fig
    
    fig, ax = plt.subplots(figsize=(12, 5))
    
    ax.bar(
        hourly_data["Hour of Day"],
        hourly_data["alert_count"],
        color="#10b981",
        edgecolor="black",
        linewidth=0.8
    )
    
    ax.set_xlabel("Hour of Day", fontsize=11)
    ax.set_ylabel("Number of Alerts", fontsize=11)
    ax.set_title("Alert Distribution by Hour of Day", fontsize=13, fontweight="bold")
    ax.grid(True, alpha=0.3, axis="y")
    ax.set_xticks(range(0, 24, 2))
    plt.tight_layout()
    
    return fig


def create_oblast_comparison_chart(comparison_df: pd.DataFrame) -> plt.Figure:
    """Create bar chart comparing alert counts across oblasts."""
    if comparison_df.empty:
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.text(0.5, 0.5, "No data available", ha="center", va="center")
        return fig
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    sorted_df = comparison_df.sort_values("Alert Count", ascending=True)
    
    ax.barh(
        sorted_df["Oblast"],
        sorted_df["Alert Count"],
        color="#f59e0b",
        edgecolor="black",
        linewidth=1.2
    )
    
    ax.set_xlabel("Number of Alerts", fontsize=11)
    ax.set_title("Alert Count Comparison by Oblast", fontsize=13, fontweight="bold")
    ax.grid(True, alpha=0.3, axis="x")
    plt.tight_layout()
    
    return fig
