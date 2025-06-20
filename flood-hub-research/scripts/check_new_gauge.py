#!/usr/bin/env python3
"""
Check details of newly discovered gauge
"""

import requests
import json

API_KEY = "AIzaSyB0d7jLuqXjDJW_BQxOyCrBVt97zse7S-M"
BASE_URL = "https://floodforecasting.googleapis.com/v1"

def check_gauge_details(gauge_id):
    """Get detailed information about a gauge"""
    
    headers = {'X-goog-api-key': API_KEY}
    
    # Get gauge metadata
    print(f"📍 Checking gauge: {gauge_id}")
    print("="*50)
    
    url = f"{BASE_URL}/gauges/{gauge_id}"
    params = {'key': API_KEY}
    
    response = requests.get(url, params=params, headers=headers)
    if response.status_code == 200:
        gauge = response.json()
        
        print(f"\n✅ GAUGE METADATA:")
        print(f"ID: {gauge.get('gaugeId')}")
        print(f"Location: {gauge.get('location', {}).get('latitude')}, {gauge.get('location', {}).get('longitude')}")
        print(f"River: {gauge.get('river', 'Not specified')}")
        print(f"Site Name: {gauge.get('siteName', 'Not specified')}")
        print(f"Source: {gauge.get('source')}")
        print(f"Quality Verified: {gauge.get('qualityVerified')}")
        print(f"Has Model: {gauge.get('hasModel')}")
        
        # Get model data
        model_url = f"{BASE_URL}/gaugeModels/{gauge_id}"
        model_response = requests.get(model_url, params=params, headers=headers)
        
        if model_response.status_code == 200:
            model = model_response.json()
            print(f"\n📊 FLOOD THRESHOLDS:")
            thresholds = model.get('thresholds', {})
            print(f"Warning Level: {thresholds.get('warningLevel', 'N/A')} {model.get('gaugeValueUnit', '')}")
            print(f"Danger Level: {thresholds.get('dangerLevel', 'N/A')} {model.get('gaugeValueUnit', '')}")
            print(f"Extreme Danger: {thresholds.get('extremeDangerLevel', 'N/A')} {model.get('gaugeValueUnit', '')}")
        
        # Determine location
        lat = gauge.get('location', {}).get('latitude')
        lon = gauge.get('location', {}).get('longitude')
        
        print(f"\n📍 LOCATION ANALYSIS:")
        print(f"Coordinates: {lat}, {lon}")
        
        # Estimate province
        if lat > 35:
            province = "Gilgit-Baltistan or KPK (North)"
        elif lat > 30 and lon > 73:
            province = "Punjab"
        elif lat < 28:
            province = "Sindh"
        elif lon < 67:
            province = "Balochistan"
        else:
            province = "Central Pakistan"
        
        print(f"Estimated Province: {province}")
        
        # Distance from major cities
        cities = {
            'Islamabad': (33.6844, 73.0479),
            'Lahore': (31.5497, 74.3436),
            'Multan': (30.1575, 71.5249),
            'Faisalabad': (31.4504, 73.1350)
        }
        
        print(f"\nDistances to cities:")
        for city, (clat, clon) in cities.items():
            dist = ((lat - clat)**2 + (lon - clon)**2)**0.5 * 111
            print(f"  {city}: ~{dist:.0f} km")
        
        return gauge
    else:
        print(f"Error fetching gauge: {response.status_code}")
        return None

# Check both known Pakistani gauges
print("🔍 CHECKING PAKISTANI GAUGES")
print("="*50)

gauges = ['hybas_4121489010', 'hybas_4121491070']

for gauge_id in gauges:
    check_gauge_details(gauge_id)
    print("\n" + "="*50 + "\n")