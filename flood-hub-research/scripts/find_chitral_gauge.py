#!/usr/bin/env python3
"""
Find Chitral River gauge and verify it exists
"""

import requests
import json

API_KEY = "AIzaSyB0d7jLuqXjDJW_BQxOyCrBVt97zse7S-M"
BASE_URL = "https://floodforecasting.googleapis.com/v1"

def check_chitral_gauge():
    """Check if Chitral gauge exists"""
    
    # Known Chitral gauge ID from report
    chitral_id = "hybas_4120570410"
    
    print(f"🔍 Checking for Chitral River gauge: {chitral_id}")
    print("="*50)
    
    headers = {'X-goog-api-key': API_KEY}
    url = f"{BASE_URL}/gauges/{chitral_id}"
    params = {'key': API_KEY}
    
    try:
        response = requests.get(url, params=params, headers=headers)
        
        if response.status_code == 200:
            gauge = response.json()
            
            print("✅ CHITRAL GAUGE FOUND!")
            print(f"\nGauge Details:")
            print(f"ID: {gauge.get('gaugeId')}")
            print(f"Location: {gauge.get('location', {}).get('latitude')}, {gauge.get('location', {}).get('longitude')}")
            print(f"River: {gauge.get('river', 'Not specified')}")
            print(f"Site Name: {gauge.get('siteName', 'Not specified')}")
            print(f"Source: {gauge.get('source')}")
            print(f"Quality Verified: {gauge.get('qualityVerified')}")
            print(f"Has Model: {gauge.get('hasModel')}")
            
            # Check if in Pakistan
            lat = gauge.get('location', {}).get('latitude', 0)
            lon = gauge.get('location', {}).get('longitude', 0)
            
            if 23 <= lat <= 37 and 60 <= lon <= 77:
                print(f"\n✓ Confirmed: Gauge is within Pakistan bounds")
                
                # Get thresholds
                model_url = f"{BASE_URL}/gaugeModels/{chitral_id}"
                model_response = requests.get(model_url, params=params, headers=headers)
                
                if model_response.status_code == 200:
                    model = model_response.json()
                    print(f"\n📊 Flood Thresholds:")
                    thresholds = model.get('thresholds', {})
                    unit = model.get('gaugeValueUnit', '')
                    print(f"Warning Level: {thresholds.get('warningLevel', 'N/A')} {unit}")
                    print(f"Danger Level: {thresholds.get('dangerLevel', 'N/A')} {unit}")
                    print(f"Extreme Danger: {thresholds.get('extremeDangerLevel', 'N/A')} {unit}")
            else:
                print(f"\n⚠️ Gauge location ({lat}, {lon}) is outside Pakistan bounds")
        else:
            print(f"❌ Chitral gauge not found. Status: {response.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")

# Also check our discovery results
print("\n📊 ANALYZING DISCOVERY RESULTS")
print("="*50)

try:
    with open('pakistan_gauges_full_20250620_151614.json', 'r') as f:
        data = json.load(f)
    
    gauges = data['gauges']
    print(f"Total gauges discovered: {len(gauges)}")
    
    # Look for northern gauges (Chitral is in north)
    northern_gauges = [g for g in gauges if g.get('location', {}).get('latitude', 0) > 35]
    print(f"Gauges in far north (>35°N): {len(northern_gauges)}")
    
    # Check if any match Chitral pattern
    chitral_pattern_gauges = [g for g in gauges if '412057' in g.get('gaugeId', '')]
    print(f"Gauges matching Chitral pattern: {len(chitral_pattern_gauges)}")
    
except:
    print("Could not load discovery results")

print("\n" + "="*50)
check_chitral_gauge()