#!/usr/bin/env python3
"""
Emergency Flood Verification for Chitral River Gauge
Gauge ID: hybas_4120570410
Run: python3 scripts/chitral_flood_check.py
"""

import json
import sys
from datetime import datetime, timezone
import urllib.request
import urllib.parse

# Configuration
GAUGE_ID = "hybas_4120570410"
API_KEY = "AIzaSyB0d7jLuqXjDJW_BQxOyCrBVt97zse7S-M"
BASE_URL = "https://floodforecasting.googleapis.com/v1"
FLOOD_HUB_URL = "https://sites.research.google/floods/l/36.38591277287651/72.2021484375/10/g/hybas_4120570410"

def make_api_request(endpoint, params=None):
    """Make API request using urllib (no external dependencies)"""
    url = f"{BASE_URL}/{endpoint}"
    
    if params is None:
        params = {}
    params['key'] = API_KEY
    
    query_string = urllib.parse.urlencode(params)
    full_url = f"{url}?{query_string}"
    
    try:
        with urllib.request.urlopen(full_url) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"Error making request to {endpoint}: {e}")
        return None

def check_gauge_status():
    """Pull all relevant data for the Chitral gauge"""
    
    print(f"🚨 CHITRAL RIVER FLOOD CHECK: {GAUGE_ID}")
    print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
    print("="*60)
    
    # 1. Get gauge details
    print("\n📍 GAUGE DETAILS:")
    gauge_info = make_api_request(f"gauges/{GAUGE_ID}")
    if gauge_info:
        print(f"  Location: {gauge_info.get('location', {}).get('latitude', 'N/A')}, {gauge_info.get('location', {}).get('longitude', 'N/A')}")
        print(f"  Site Name: {gauge_info.get('siteName', 'N/A')}")
        print(f"  River: {gauge_info.get('river', 'N/A')}")
        print(f"  Quality Verified: {gauge_info.get('qualityVerified', 'N/A')}")
        print(f"  Has Model: {gauge_info.get('hasModel', 'N/A')}")
        print(f"  Source: {gauge_info.get('source', 'N/A')}")
    else:
        print("  ❌ Failed to retrieve gauge details")
    
    # 2. Get current flood status
    print("\n🌊 CURRENT FLOOD STATUS:")
    flood_status = make_api_request("floodStatus", {"gaugeId": GAUGE_ID})
    if flood_status:
        # Handle response based on structure
        if isinstance(flood_status, list) and flood_status:
            status = flood_status[0]
        elif isinstance(flood_status, dict):
            status = flood_status
        else:
            status = None
            
        if status:
            print(f"  Severity: {status.get('severity', 'N/A')}")
            print(f"  Gauge Value Unit: {status.get('gaugeValueUnit', 'N/A')}")
            
            # Thresholds
            thresholds = status.get('thresholds', {})
            if thresholds:
                print(f"\n  📊 THRESHOLDS:")
                print(f"    Warning Level: {thresholds.get('warningLevel', 'N/A')} m³/s")
                print(f"    Danger Level: {thresholds.get('dangerLevel', 'N/A')} m³/s")
                print(f"    Extreme Danger Level: {thresholds.get('extremeDangerLevel', 'N/A')} m³/s")
            
            # Predictions
            predictions = status.get('predictions', [])
            if predictions:
                print(f"\n  📈 FORECAST (Next {len(predictions)} time steps):")
                for i, pred in enumerate(predictions[:5]):  # Show first 5 predictions
                    time_str = pred.get('time', 'N/A')
                    value = pred.get('value', 'N/A')
                    print(f"    {i+1}. {time_str}: {value} m³/s")
                    
                    # Check if crossing thresholds
                    if thresholds and value != 'N/A':
                        if value >= thresholds.get('extremeDangerLevel', float('inf')):
                            print(f"       ⚠️  EXTREME DANGER LEVEL!")
                        elif value >= thresholds.get('dangerLevel', float('inf')):
                            print(f"       ⚠️  DANGER LEVEL!")
                        elif value >= thresholds.get('warningLevel', float('inf')):
                            print(f"       ⚠️  WARNING LEVEL!")
    else:
        print("  ❌ Failed to retrieve flood status")
    
    # 3. Get gauge model/thresholds
    print("\n📐 GAUGE MODEL DATA:")
    gauge_model = make_api_request(f"gaugeModels/{GAUGE_ID}")
    if gauge_model:
        print(f"  Model Type: {gauge_model.get('modelType', 'N/A')}")
        print(f"  Last Update: {gauge_model.get('lastUpdateTime', 'N/A')}")
        
        # Return periods
        return_periods = gauge_model.get('returnPeriods', {})
        if return_periods:
            print(f"\n  Return Periods:")
            print(f"    2-year: {return_periods.get('twoYear', 'N/A')} m³/s")
            print(f"    5-year: {return_periods.get('fiveYear', 'N/A')} m³/s")
            print(f"    20-year: {return_periods.get('twentyYear', 'N/A')} m³/s")
    else:
        print("  ❌ Failed to retrieve gauge model")
    
    # 4. Summary and recommendations
    print("\n" + "="*60)
    print("📋 SUMMARY:")
    
    if gauge_info and gauge_info.get('qualityVerified'):
        print("  ✅ Gauge is quality verified")
    else:
        print("  ⚠️  Gauge quality not verified")
        
    if flood_status:
        print(f"  📊 Current severity: {status.get('severity', 'UNKNOWN')}")
        
    print(f"\n🔗 View on Google Flood Hub:")
    print(f"  {FLOOD_HUB_URL}")
    
    # Export raw data
    print("\n💾 Exporting raw data to chitral_flood_data.json...")
    export_data = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "gauge_id": GAUGE_ID,
        "gauge_info": gauge_info,
        "flood_status": flood_status,
        "gauge_model": gauge_model
    }
    
    with open("chitral_flood_data.json", "w") as f:
        json.dump(export_data, f, indent=2)
    print("  ✅ Data exported successfully")

def main():
    """Main execution"""
    try:
        check_gauge_status()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()