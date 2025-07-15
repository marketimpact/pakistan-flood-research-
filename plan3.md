# How to Identify Physical River Gauges for Pakistan in Google Flood Hub

## Step-by-Step Verification Process

### 1. Query All Pakistani Gauges

First, you'll need to get all gauges within Pakistan's boundaries. Use the Google Flood Hub API with a bounding box query:

```python
# Pakistan approximate bounding box
pakistan_bounds = {
    "min_lat": 23.5,
    "max_lat": 37.5,
    "min_lon": 60.5,
    "max_lon": 77.5
}

# API endpoint (example structure - check current docs)
GET /v1/gauges?bounds={pakistan_bounds}
```

### 2. Identify Physical Gauge Indicators

Physical gauges typically have these characteristics:

#### A. Check the `source` field
```json
{
    "source": "GRDC",  // Physical network
    "source": "WAPDA", // Pakistan's Water and Power Development Authority
    "source": "PMD",   // Pakistan Meteorological Department
    "source": "HYBAS"  // Could be either physical or virtual
}
```

#### B. Look for `siteName` or `river` fields
Physical gauges usually have:
```json
{
    "siteName": "Tarbela Dam",
    "river": "Indus River"
}
```

Virtual gauges typically show:
```json
{
    "siteName": "",
    "river": ""
}
```

#### C. Analyze the `gaugeId` format
- **GRDC Format:** `PKGR####` or similar (PK for Pakistan)
- **National Format:** May include station codes
- **HYBAS Format:** `hybas_#########` (needs further verification)

### 3. Create a Verification Script

Here's a Python approach to categorize gauges:

```python
import requests
import json
import pandas as pd

def analyze_pakistan_gauges():
    # Fetch all Pakistani gauges
    gauges = fetch_pakistan_gauges()  # Your API call
    
    physical_indicators = []
    
    for gauge in gauges:
        confidence_score = 0
        evidence = []
        
        # Check 1: Named site or river
        if gauge.get('siteName', '').strip():
            confidence_score += 30
            evidence.append(f"Named site: {gauge['siteName']}")
        
        if gauge.get('river', '').strip():
            confidence_score += 20
            evidence.append(f"Named river: {gauge['river']}")
        
        # Check 2: Source type
        source = gauge.get('source', '')
        if source in ['GRDC', 'WAPDA', 'PMD']:
            confidence_score += 40
            evidence.append(f"Physical network: {source}")
        elif source == 'HYBAS':
            # HYBAS needs additional verification
            confidence_score += 10
            evidence.append("HYBAS - needs verification")
        
        # Check 3: Quality verified
        if gauge.get('qualityVerified', False):
            confidence_score += 10
            evidence.append("Quality verified")
        
        # Check 4: Gauge ID pattern
        gauge_id = gauge.get('gaugeId', '')
        if not gauge_id.startswith('hybas_'):
            confidence_score += 20
            evidence.append("Non-HYBAS ID format")
        
        physical_indicators.append({
            'gaugeId': gauge_id,
            'location': gauge.get('location'),
            'confidence_score': confidence_score,
            'likely_physical': confidence_score >= 50,
            'evidence': '; '.join(evidence)
        })
    
    return pd.DataFrame(physical_indicators)
```

### 4. Cross-Reference with Known Pakistani Stations

Compare your results with known physical gauges in Pakistan:

#### Major Physical Stations (to verify against):
- **Indus River:** Tarbela, Kalabagh, Chashma, Sukkur, Kotri
- **Chenab River:** Marala, Khanki, Qadirabad
- **Jhelum River:** Mangla, Rasul
- **Kabul River:** Nowshera
- **Sutlej River:** Sulemanki

### 5. Contact Google for Clarification

Based on the GiveDirectly meeting notes, Google has been responsive to partner queries:

```python
# Prepare a structured query for Google
uncertain_gauges = df[df['confidence_score'].between(30, 70)]

email_to_google = f"""
We are implementing flood early warning for Pakistan and need clarification on gauge types:

High-confidence physical gauges identified: {len(df[df['confidence_score'] > 70])}
Uncertain gauges needing verification: {len(uncertain_gauges)}

Specific questions:
1. Which HYBAS gauges in Pakistan have physical sensors?
2. Can you confirm if these gauges are virtual: {list(uncertain_gauges['gaugeId'])}
3. What does qualityVerified=true mean for HYBAS sources?
"""
```

### 6. Validation Through External Sources

Cross-check with Pakistani databases:

```python
# Check against WAPDA public data
wapda_stations = [
    # Get list from http://www.wapda.gov.pk/
]

# Check against FFD (Federal Flood Division)
ffd_stations = [
    # Get list from FFD reports
]

# Match coordinates (within ~1km tolerance)
def match_coordinates(google_gauge, known_stations, tolerance_km=1):
    # Implementation to match lat/lon
    pass
```

### 7. Create a Classification System

For your Django implementation:

```python
class GaugeClassification:
    VERIFIED_PHYSICAL = "verified_physical"      # 100% certain
    LIKELY_PHYSICAL = "likely_physical"          # 70%+ confidence
    UNCERTAIN = "uncertain"                      # 30-70% confidence  
    LIKELY_VIRTUAL = "likely_virtual"            # <30% confidence
    
    @staticmethod
    def classify(gauge_data):
        # Apply the logic from step 3
        pass
```

### 8. Manual Verification Steps

For high-priority gauges that remain uncertain:

1. **Check satellite imagery** at gauge coordinates for infrastructure
2. **Contact local PDMA/NDMA** to verify station existence
3. **Search Pakistani news** for mentions of specific gauge stations
4. **Review WAPDA annual reports** for station lists

### 9. Document Your Findings

Create a reference table:

| Gauge ID | Coordinates | Source | Site Name | Classification | Evidence | Last Verified |
|----------|-------------|---------|-----------|----------------|----------|---------------|
| PKGR0012 | 31.45, 72.3 | GRDC | Marala Headworks | verified_physical | Named site, GRDC network | 2025-07-01 |
| hybas_4121489010 | 26.06, 68.93 | HYBAS | | likely_virtual | No site name, HYBAS only | 2025-07-01 |

### 10. Recommended Approach for Pak-FEWS

Given your timeline and budget constraints:

1. **Start with obvious physical gauges** (confidence score > 70)
2. **Include high-quality HYBAS gauges** where `qualityVerified=true`
3. **Flag uncertain gauges** in your interface (e.g., "AI-predicted" label)
4. **Build in user feedback** to report gauge accuracy

```python
# In your Django model
class RiverGauge(models.Model):
    gauge_id = models.CharField(max_length=50, unique=True)
    classification = models.CharField(max_length=20)
    confidence_score = models.IntegerField()
    evidence = models.TextField()
    last_verified = models.DateTimeField()
    user_feedback_count = models.IntegerField(default=0)
    accuracy_rating = models.FloatField(null=True)
```

This systematic approach will help you identify which Pakistani gauges are physical versus virtual, enabling appropriate trust levels in your alert system.