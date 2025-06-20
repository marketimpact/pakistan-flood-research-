# Google Flood Hub Pakistan Research Project

## Project Overview
You are helping research and develop Pak-FEWS (Pakistan Flood Early Warning System), a lightweight flood monitoring system using Google Flood Hub API data. The goal is to provide 24-hour advance flood warnings for Pakistan, improving on current 10-day delays.

## Your Task
Conduct systematic research on Google Flood Hub API coverage and capabilities for Pakistan. This research will inform system design decisions for a Django-based monitoring and alerting platform.

## Key Research Questions

### 1. Pakistani Gauge Inventory
- Query all gauges within Pakistan (lat: 23-37°N, lon: 60-77°E)
- Document total count and geographic distribution
- Identify which gauges have `qualityVerified: true`
- Map which gauges have `hasModel: true`
- Note which provide inundation maps vs gauge-only data

### 2. Data Quality Investigation
- What does `qualityVerified` actually mean?
- What criteria must a gauge meet for this designation?
- How many Pakistani gauges meet this standard?

### 3. Alert Thresholds Analysis
- How are Warning/Danger/ExtremeDanger levels calculated?
- What do 2/5/20-year return periods mean in practical terms?
- Document actual threshold values for major Pakistani rivers

### 4. Severity and Probability Mapping
- What does severity (SEVERE, etc.) represent?
- For probability maps: what do HIGH/MEDIUM/LOW mean?
- When are PROBABILITY vs DEPTH maps available?

### 5. Coverage Assessment
- Which major Pakistani rivers have coverage?
- Focus on: Indus, Jhelum, Chenab, Ravi, Sutlej
- Identify any critical gaps in flood-prone areas

## API Information
- Documentation: https://developers.google.com/flood-forecasting/
- Key endpoints:
  - GET /v1/gauges (list gauges)
  - GET /v1/gauges/{gaugeId} (gauge details)
  - GET /v1/floodStatus (flood predictions)
  - GET /v1/gaugeModels/{gaugeId} (threshold data)

## Required Outputs
1. **gauge_inventory.csv** - All Pakistani gauges with metadata
2. **coverage_analysis.json** - Statistical summary of coverage
3. **threshold_analysis.csv** - Threshold values for major gauges
4. **research_findings.md** - Comprehensive report answering all questions
5. **coverage_map.html** - Visual map of gauge locations

## Technical Context
- Budget constraint: <$10,000 total project
- Timeline: Research due by June 25, 2025
- System must be lightweight and simple
- Target users have limited technical capacity
- Must complement (not replace) existing NDMA systems

## Example API Responses
```json
// Gauge Model
{
    "location": {"latitude": 26.060416666665333, "longitude": 68.931249999995941},
    "siteName": "",
    "source": "HYBAS",
    "river": "",
    "gaugeId": "hybas_4121489010",
    "qualityVerified": true,
    "hasModel": true
}

// Flood Status
{
    "gaugeId": "hybas_6120111530",
    "severity": "SEVERE",
    "thresholds": {
        "warningLevel": 5511.65283203125,
        "dangerLevel": 6067.77880859375,
        "extremeDangerLevel": 6575.48388671875
    },
    "gaugeValueUnit": "CUBIC_METERS_PER_SECOND"
}
```

## Important Notes
- Focus only on `qualityVerified: true` gauges for the system
- Document any API limitations or unexpected behaviors
- Note patterns in data availability (why some areas lack maps)
- Consider monsoon seasonality in your analysis