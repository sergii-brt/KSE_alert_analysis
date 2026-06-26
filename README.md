# Ukrainian Air Raid Alert Analysis

A production-quality Python application for historical time-series analysis of 
Ukrainian air raid patterns by region.

## 🎯 Purpose

This application provides **historical analytical insights** into Ukrainian air raid 
patterns to help users:

- Compare air raid frequency and duration across regions
- Identify temporal patterns (monthly trends, weekday patterns, hourly distribution)
- Understand regional variations in alert activity
- Access deterministic historical statistics

**Important:** This application analyzes *historical patterns only* and does not 
forecast future events.

## ✨ Features

### 1. **Automatic Data Acquisition**
- Fetches data from the public [sirens.in.ua API](https://sirens.in.ua)
- No authentication required
- Local JSON caching with 24-hour expiry (configurable)
- Graceful fallback to cached data if API is unavailable
- Manual refresh button to force data update

### 2. **Regional Comparison**
- Compare 1-25 Ukrainian oblasts (regions)
- Metrics: alert count, average duration, total duration, longest alert
- Interactive selection via Streamlit sidebar
- Visual comparison charts

### 3. **Time Period Selection**
- Last Month (30 days)
- Last Year (365 days)
- Custom date range
- All analytics respect selected period

### 4. **Historical Time-Series Analysis**
- **Monthly trend**: Visualization of alert frequency over time
- **Weekday distribution**: Pattern analysis by day of week
- **Hourly distribution**: Pattern analysis by hour of day
- Clear, readable matplotlib charts

### 5. **Notable Historical Events**
- Longest single alert (duration)
- Day with highest alert count
- Month with highest activity
- Deterministic, data-driven statistics only

### 6. **Analytical Summary**
- Auto-generated textual summary of observed patterns
- Regional comparisons and temporal observations
- Historical facts only; no speculation or forecasting

### 7. **Reliability & Error Handling**
- Graceful handling of network failures
- Informative user-friendly error messages
- Data validation on load
- Cache corruption detection

## 📊 Dataset

**Source:** [sirens.in.ua API](https://sirens.in.ua)

**Why this dataset:**
- ✅ Public, no authentication required
- ✅ Actively maintained since 2022
- ✅ Historical data spanning 2+ years
- ✅ Regional granularity (25 Ukrainian oblasts)
- ✅ Second-level timestamp precision
- ✅ Reliable infrastructure

**Data structure:**
```json
{
  "id": "unique-identifier",
  "title": "Air raid alert",
  "location_title": "Kyiv Oblast",
  "started_at": "2024-01-15T10:00:00Z",
  "finished_at": "2024-01-15T11:00:00Z",
  "latitude": 50.45,
  "longitude": 30.52
}
