"""
Data loading and caching module for Ukrainian air raid alerts.

Handles API communication, local caching, and data validation.
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import pandas as pd
import requests

# Configuration
CACHE_DIR = Path("cache")
CACHE_FILE = CACHE_DIR / "alerts.json"
CACHE_EXPIRY_HOURS = 24
API_URL = "https://sirens.in.ua/api/v3/alerts"
TIMEOUT_SECONDS = 10


def ensure_cache_dir() -> None:
    """Create cache directory if it doesn't exist."""
    CACHE_DIR.mkdir(exist_ok=True)


def is_cache_valid() -> bool:
    """Check if cached data exists and is within expiry window."""
    if not CACHE_FILE.exists():
        return False
    
    file_time = datetime.fromtimestamp(CACHE_FILE.stat().st_mtime)
    age_hours = (datetime.now() - file_time).total_seconds() / 3600
    return age_hours < CACHE_EXPIRY_HOURS


def load_from_cache() -> Optional[list[dict]]:
    """Load alerts from local cache file."""
    if not CACHE_FILE.exists():
        return None
    
    try:
        with open(CACHE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list) and len(data) > 0:
            return data
    except (json.JSONDecodeError, IOError):
        pass
    
    return None


def save_to_cache(data: list[dict]) -> bool:
    """Save alerts to local cache file."""
    ensure_cache_dir()
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except IOError:
        return False


def fetch_from_api() -> Optional[list[dict]]:
    """Fetch alerts from the remote API."""
    try:
        response = requests.get(API_URL, timeout=TIMEOUT_SECONDS)
        response.raise_for_status()
        data = response.json()
        
        if isinstance(data, list):
            return data
    except requests.exceptions.RequestException:
        pass
    
    return None


def load_alerts(force_refresh: bool = False) -> tuple[pd.DataFrame, str]:
    """
    Load alerts from API or cache.
    
    Args:
        force_refresh: If True, skip cache and fetch from API.
    
    Returns:
        Tuple of (DataFrame with alerts, status message).
    """
    ensure_cache_dir()
    data = None
    status = ""
    
    # Try fresh API fetch if requested
    if force_refresh:
        data = fetch_from_api()
        if data:
            save_to_cache(data)
            status = "✅ Data refreshed from API"
        else:
            # Fall back to cache if API fails
            data = load_from_cache()
            if data:
                status = "⚠️ API unavailable; using cached data"
            else:
                status = "❌ No data available (API unreachable, cache empty)"
    else:
        # Use cache if valid
        if is_cache_valid():
            data = load_from_cache()
            if data:
                status = "📦 Using cached data (fresh)"
        else:
            # Cache expired, try API
            data = fetch_from_api()
            if data:
                save_to_cache(data)
                status = "✅ Data refreshed from API"
            else:
                # Fall back to stale cache
                data = load_from_cache()
                if data:
                    status = "⚠️ API unavailable; using cached data (stale)"
                else:
                    status = "❌ No data available"
    
    # Convert to DataFrame
    if not data:
        return pd.DataFrame(), status
    
    df = pd.DataFrame(data)
    
    # Validate and parse timestamps
    try:
        df["started_at"] = pd.to_datetime(df["started_at"])
        df["finished_at"] = pd.to_datetime(df["finished_at"])
        
        # For ongoing alerts, use current time as end
        now = datetime.now(df["finished_at"].dt.tz).replace(tzinfo=None)
        df["finished_at"] = df["finished_at"].fillna(now)
        
        # Ensure timezone-naive for consistency
        df["started_at"] = df["started_at"].dt.tz_localize(None)
        df["finished_at"] = df["finished_at"].dt.tz_localize(None)
        
        # Calculate duration in minutes
        df["duration_minutes"] = (df["finished_at"] - df["started_at"]).dt.total_seconds() / 60
        df["duration_minutes"] = df["duration_minutes"].clip(lower=0)
        
        # Standardize location title
        df["location_title"] = df["location_title"].str.strip()
        
        return df, status
    except (KeyError, TypeError) as e:
        return pd.DataFrame(), f"❌ Error parsing data: {str(e)}"


def get_available_oblasts(df: pd.DataFrame) -> list[str]:
    """Get sorted list of available Ukrainian oblasts."""
    if df.empty:
        return []
    
    oblasts = sorted(df["location_title"].unique().tolist())
    return oblasts
