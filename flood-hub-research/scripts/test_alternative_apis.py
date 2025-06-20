#!/usr/bin/env python3
"""
Test Alternative Flood Monitoring APIs
Since Google Flood Hub requires special access, test other available APIs
"""

import requests
import json
from datetime import datetime, timedelta


def test_open_meteo_flood_api():
    """Test Open-Meteo Flood API for Pakistan"""
    print("Testing Open-Meteo Flood API...")
    
    # Test coordinates in Pakistan (Karachi area)
    lat, lon = 24.8607, 67.0011
    
    url = "https://flood-api.open-meteo.com/v1/flood"
    params = {
        'latitude': lat,
        'longitude': lon,
        'daily': 'river_discharge',
        'past_days': 7,
        'forecast_days': 7
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        print(f"✓ Open-Meteo API working")
        print(f"Location: {data.get('latitude', 'N/A')}, {data.get('longitude', 'N/A')}")
        print(f"Timezone: {data.get('timezone', 'N/A')}")
        
        if 'daily' in data:
            print(f"Daily data points: {len(data['daily']['time'])}")
            print(f"River discharge unit: {data.get('daily_units', {}).get('river_discharge', 'N/A')}")
        
        return True, data
        
    except Exception as e:
        print(f"✗ Open-Meteo API failed: {e}")
        return False, None


def test_usgs_water_services():
    """Test USGS Water Services API (for comparison/reference)"""
    print("\nTesting USGS Water Services API...")
    
    # Test with a US site for comparison (won't have Pakistan data)
    url = "https://waterservices.usgs.gov/nwis/iv/"
    params = {
        'format': 'json',
        'sites': '01646500',  # Potomac River example
        'period': 'P1D',
        'parameterCd': '00065'  # Gauge height
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        print(f"✓ USGS API working (US reference)")
        if 'value' in data and 'timeSeries' in data['value']:
            print(f"Time series count: {len(data['value']['timeSeries'])}")
        
        return True, data
        
    except Exception as e:
        print(f"✗ USGS API failed: {e}")
        return False, None


def test_google_api_general_access():
    """Test if the Google API key works with other Google APIs"""
    print("\nTesting Google API key with Google Maps Geocoding...")
    
    api_key = "AIzaSyB0d7jLuqXjDJW_BQxOyCrBVt97zse7S-M"
    
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        'address': 'Islamabad, Pakistan',
        'key': api_key
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        if data['status'] == 'OK':
            print(f"✓ Google API key is valid and working")
            location = data['results'][0]['geometry']['location']
            print(f"Islamabad coordinates: {location['lat']}, {location['lng']}")
            return True, data
        else:
            print(f"✗ Google API returned status: {data['status']}")
            return False, data
            
    except Exception as e:
        print(f"✗ Google API test failed: {e}")
        return False, None


def test_flood_hub_with_specific_gauge():
    """Try Google Flood Hub with a specific gauge ID from documentation"""
    print("\nTesting Google Flood Hub with specific gauge ID...")
    
    api_key = "AIzaSyB0d7jLuqXjDJW_BQxOyCrBVt97zse7S-M"
    
    # Try the gauge ID from CLAUDE.md documentation
    gauge_id = "hybas_4121489010"
    
    url = f"https://floodforecasting.googleapis.com/v1/gauges/{gauge_id}"
    
    # Try both authentication methods
    methods = [
        {"headers": {"X-goog-api-key": api_key}, "params": {}},
        {"headers": {}, "params": {"key": api_key}}
    ]
    
    for i, auth_method in enumerate(methods, 1):
        try:
            print(f"  Attempt {i}: {'Header' if auth_method['headers'] else 'Parameter'} auth")
            response = requests.get(url, **auth_method)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✓ Success! Gauge data retrieved")
                print(f"Gauge ID: {data.get('gaugeId', 'N/A')}")
                print(f"Location: {data.get('location', {})}")
                print(f"River: {data.get('river', 'N/A')}")
                return True, data
            else:
                print(f"  Status: {response.status_code}")
                if response.status_code == 403:
                    print(f"  Message: API access forbidden - may need approval")
                elif response.status_code == 404:
                    print(f"  Message: Gauge not found or endpoint incorrect")
                    
        except Exception as e:
            print(f"  Error: {e}")
    
    print("✗ All attempts failed")
    return False, None


def main():
    """Test all available APIs"""
    print("Pakistan Flood Monitoring API Testing")
    print("=" * 50)
    
    results = {}
    
    # Test alternative APIs
    results['open_meteo'] = test_open_meteo_flood_api()
    results['usgs'] = test_usgs_water_services()
    results['google_general'] = test_google_api_general_access()
    results['flood_hub'] = test_flood_hub_with_specific_gauge()
    
    # Summary
    print("\n" + "=" * 50)
    print("API TESTING SUMMARY")
    print("=" * 50)
    
    for api_name, (success, data) in results.items():
        status = "✓ Working" if success else "✗ Failed"
        print(f"{api_name.replace('_', ' ').title()}: {status}")
    
    # Recommendations
    print("\nRECOMMENDATIONS:")
    if results['google_general'][0]:
        print("• Google API key is valid - Flood Hub may need approval")
    if results['open_meteo'][0]:
        print("• Open-Meteo can be used as alternative for flood data")
    if not results['flood_hub'][0]:
        print("• Apply for Google Flood Hub pilot program access")
        print("• Consider using Open-Meteo or Google Earth Engine for now")


if __name__ == "__main__":
    main()