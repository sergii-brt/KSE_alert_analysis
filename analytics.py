"""
Time-series analysis functions for air raid alerts.

Provides temporal decomposition, statistics, and comparison metrics.
"""

from datetime import datetime
from typing import Optional

import pandas as pd


def filter_by_date_range(
    df: pd.DataFrame, 
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> pd.DataFrame:
    """Filter alerts by date range."""
    if df.empty:
        return df
    
    result = df.copy()
    
    if start_date:
        result = result[result["started_at"] >= start_date]
    
    if end_date:
        result = result[result["started_at"] <= end_date]
    
    return result


def filter_by_oblasts(df: pd.DataFrame, oblasts: list[str]) -> pd.DataFrame:
    """Filter alerts by oblast names."""
    if df.empty or not oblasts:
        return df
    
    return df[df["location_title"].isin(oblasts)]


def get_summary_statistics(df: pd.DataFrame) -> dict:
    """Calculate overall summary statistics."""
    if df.empty:
        return {
            "total_alerts": 0,
            "unique_oblasts": 0,
            "date_range": "No data",
            "avg_duration_minutes": 0,
            "total_duration_hours": 0,
            "longest_alert_minutes": 0,
        }
    
    duration_hours = df["duration_minutes"].sum() / 60
    
    return {
        "total_alerts": len(df),
        "unique_oblasts": df["location_title"].nunique(),
        "date_range": f"{df['started_at'].min().date()} to {df['started_at'].max().date()}",
        "avg_duration_minutes": round(df["duration_minutes"].mean(), 1),
        "total_duration_hours": round(duration_hours, 1),
        "longest_alert_minutes": round(df["duration_minutes"].max(), 1),
    }


def get_oblast_comparison(df: pd.DataFrame, oblasts: list[str]) -> pd.DataFrame:
    """Generate comparison metrics for selected oblasts."""
    if df.empty:
        return pd.DataFrame()
    
    result_data = []
    
    for oblast in oblasts:
        oblast_df = df[df["location_title"] == oblast]
        
        if oblast_df.empty:
            continue
        
        result_data.append({
            "Oblast": oblast,
            "Alert Count": len(oblast_df),
            "Avg Duration (min)": round(oblast_df["duration_minutes"].mean(), 1),
            "Total Duration (hours)": round(oblast_df["duration_minutes"].sum() / 60, 1),
            "Longest Alert (min)": round(oblast_df["duration_minutes"].max(), 1),
            "First Alert": oblast_df["started_at"].min().date(),
            "Last Alert": oblast_df["started_at"].max().date(),
        })
    
    return pd.DataFrame(result_data)


def get_monthly_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """Get alert counts by month."""
    if df.empty:
        return pd.DataFrame()
    
    df_copy = df.copy()
    df_copy["month"] = df_copy["started_at"].dt.to_period("M")
    
    monthly = df_copy.groupby("month").agg({
        "id": "count",
        "duration_minutes": "sum"
    }).rename(columns={"id": "alert_count", "duration_minutes": "total_duration_min"})
    
    monthly["month_str"] = monthly.index.strftime("%Y-%m")
    monthly = monthly.reset_index(drop=True)
    
    return monthly[["month_str", "alert_count", "total_duration_min"]]


def get_weekday_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """Get alert counts by day of week."""
    if df.empty:
        return pd.DataFrame()
    
    df_copy = df.copy()
    weekday_map = {0: "Monday", 1: "Tuesday", 2: "Wednesday", 3: "Thursday", 
                   4: "Friday", 5: "Saturday", 6: "Sunday"}
    df_copy["weekday"] = df_copy["started_at"].dt.dayofweek.map(weekday_map)
    
    weekday_dist = df_copy.groupby("weekday").agg({
        "id": "count",
        "duration_minutes": "mean"
    }).rename(columns={"id": "alert_count", "duration_minutes": "avg_duration_min"})
    
    # Reorder by day of week
    weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    weekday_dist = weekday_dist.reindex([d for d in weekday_order if d in weekday_dist.index])
    
    return weekday_dist.reset_index().rename(columns={"weekday": "Day of Week"})


def get_hourly_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """Get alert counts by hour of day."""
    if df.empty:
        return pd.DataFrame()
    
    df_copy = df.copy()
    df_copy["hour"] = df_copy["started_at"].dt.hour
    
    hourly = df_copy.groupby("hour").agg({
        "id": "count",
        "duration_minutes": "mean"
    }).rename(columns={"id": "alert_count", "duration_minutes": "avg_duration_min"})
    
    return hourly.reset_index().rename(columns={"hour": "Hour of Day"})


def get_notable_events(df: pd.DataFrame) -> dict:
    """Extract notable historical events from data."""
    if df.empty:
        return {
            "longest_alert": "No data",
            "day_highest_alerts": "No data",
            "month_highest_activity": "No data",
        }
    
    # Longest alert
    longest_idx = df["duration_minutes"].idxmax()
    longest_alert = df.loc[longest_idx]
    longest_info = (
        f"{longest_alert['location_title']}: "
        f"{longest_alert['started_at'].date()} "
        f"({round(longest_alert['duration_minutes'], 1)} minutes)"
    )
    
    # Day with most alerts
    daily_counts = df.groupby(df["started_at"].dt.date).size()
    busiest_day = daily_counts.idxmax()
    busiest_count = daily_counts.max()
    busiest_info = f"{busiest_day}: {busiest_count} alerts"
    
    # Month with most activity
    df_copy = df.copy()
    df_copy["month"] = df_copy["started_at"].dt.to_period("M")
    monthly_counts = df_copy.groupby("month").size()
    busiest_month = monthly_counts.idxmax()
    busiest_month_count = monthly_counts.max()
    busiest_month_info = f"{busiest_month}: {busiest_month_count} alerts"
    
    return {
        "longest_alert": longest_info,
        "day_highest_alerts": busiest_info,
        "month_highest_activity": busiest_month_info,
    }


def generate_analytical_summary(
    df: pd.DataFrame, 
    oblasts: list[str],
    stats: dict
) -> str:
    """
    Generate textual analytical summary of observed historical patterns.
    
    Returns only deterministic facts from data; no speculation.
    """
    if df.empty:
        return "No data available for analysis."
    
    lines = []
    lines.append("## 📊 Historical Analysis Summary")
    lines.append("")
    
    # Overall statistics
    lines.append(f"**Analysis Period:** {stats['date_range']}")
    lines.append(f"**Total Alerts Analyzed:** {stats['total_alerts']}")
    lines.append(f"**Total Alert Duration:** {stats['total_duration_hours']} hours")
    lines.append(f"**Average Alert Duration:** {stats['avg_duration_minutes']} minutes")
    lines.append("")
    
    # Regional analysis
    if len(oblasts) > 1:
        lines.append(f"### Comparison: {', '.join(oblasts)}")
        comparison = get_oblast_comparison(df, oblasts)
        
        if not comparison.empty:
            alert_counts = comparison.set_index("Oblast")["Alert Count"].to_dict()
            most_affected = max(alert_counts, key=alert_counts.get)
            least_affected = min(alert_counts, key=alert_counts.get)
            
            lines.append(
                f"**Most affected region:** {most_affected} "
                f"({alert_counts[most_affected]} alerts)"
            )
            lines.append(
                f"**Least affected region:** {least_affected} "
                f"({alert_counts[least_affected]} alerts)"
            )
            lines.append("")
    
    # Temporal patterns
    lines.append("### Temporal Patterns")
    
    weekday_dist = get_weekday_distribution(df)
    if not weekday_dist.empty:
        busiest_day = weekday_dist.loc[weekday_dist["alert_count"].idxmax(), "Day of Week"]
        lines.append(f"**Busiest day of week:** {busiest_day}")
    
    hourly_dist = get_hourly_distribution(df)
    if not hourly_dist.empty:
        busiest_hour = hourly_dist.loc[hourly_dist["alert_count"].idxmax(), "Hour of Day"]
        lines.append(f"**Busiest hour:** {int(busiest_hour)}:00 - {int(busiest_hour)+1}:00")
    
    lines.append("")
    
    # Notable events
    lines.append("### Notable Historical Events")
    notable = get_notable_events(df)
    lines.append(f"**Longest single alert:** {notable['longest_alert']}")
    lines.append(f"**Day with most alerts:** {notable['day_highest_alerts']}")
    lines.append(f"**Month with most activity:** {notable['month_highest_activity']}")
    lines.append("")
    
    # Closure note
    lines.append("*This summary describes observed historical patterns in the data. "
                 "It does not predict future events.*")
    
    return "\n".join(lines)
