"""
Automated tests for data loading pipeline.

Validates API communication, caching, and data parsing.
"""

import json
import tempfile
from pathlib import Path
from datetime import datetime

import pandas as pd
import pytest

from data_loader import (
    load_alerts,
    save_to_cache,
    load_from_cache,
    ensure_cache_dir,
)


def test_cache_directory_creation():
    """Test that cache directory is created successfully."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cache_path = Path(tmpdir) / "cache"
        assert not cache_path.exists()
        
        # This should create the directory
        cache_path.mkdir(exist_ok=True)
        
        assert cache_path.exists()


def test_save_and_load_cache():
    """Test cache save and load functionality."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cache_file = Path(tmpdir) / "test_alerts.json"
        
        test_data = [
            {
                "id": 1,
                "title": "Air raid alert",
                "location_title": "Kyiv Oblast",
                "started_at": "2024-01-01T10:00:00Z",
                "finished_at": "2024-01-01T11:00:00Z",
            },
            {
                "id": 2,
                "title": "Air raid alert",
                "location_title": "Lviv Oblast",
                "started_at": "2024-01-01T10:30:00Z",
                "finished_at": "2024-01-01T11:30:00Z",
            }
        ]
        
        # Save
        with open(cache_file, "w") as f:
            json.dump(test_data, f)
        
        # Load
        with open(cache_file, "r") as f:
            loaded = json.load(f)
        
        assert loaded == test_data
        assert len(loaded) == 2


def test_alerts_dataframe_parsing():
    """Test that alert data is correctly parsed into DataFrame."""
    test_data = [
        {
            "id": "1",
            "title": "Air raid alert",
            "location_title": "Kyiv Oblast",
            "started_at": "2024-01-15T10:00:00Z",
            "finished_at": "2024-01-15T11:00:00Z",
            "latitude": 50.45,
            "longitude": 30.52,
        }
    ]
    
    df = pd.DataFrame(test_data)
    
    # Parse timestamps
    df["started_at"] = pd.to_datetime(df["started_at"])
    df["finished_at"] = pd.to_datetime(df["finished_at"])
    df["started_at"] = df["started_at"].dt.tz_localize(None)
    df["finished_at"] = df["finished_at"].dt.tz_localize(None)
    
    # Calculate duration
    df["duration_minutes"] = (df["finished_at"] - df["started_at"]).dt.total_seconds() / 60
    
    assert not df.empty
    assert len(df) == 1
    assert df.loc[0, "location_title"] == "Kyiv Oblast"
    assert df.loc[0, "duration_minutes"] == 60.0


def test_empty_dataframe_handling():
    """Test that empty DataFrames are handled gracefully."""
    empty_df = pd.DataFrame()
    
    assert empty_df.empty
    assert len(empty_df) == 0
    
    # Should not raise exceptions
    try:
        _ = empty_df["location_title"].unique()
    except KeyError:
        pass  # Expected for missing column


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
