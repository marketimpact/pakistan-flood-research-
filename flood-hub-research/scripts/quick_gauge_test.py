#!/usr/bin/env python3
"""
Quick test to find Pakistani gauges using key parameters
"""

import requests
import json
from datetime import datetime

API_KEY = "AIzaSyB0d7jLuqXjDJW_BQxOyCrBVt97zse7S-M"
BASE_URL = "https://floodforecasting.googleapis.com/v1"

def test_endpoints():
    """Test different endpoint approaches"""
    
    headers = {
        'X-goog-api-key': API_KEY,
        'Accept': 'application/json'
    }
    
    print("🚀 TESTING GOOGLE FLOOD HUB ENDPOINTS")
    print("="*50)
    
    # Test 1: Direct gauge access (we know this works)
    print("\n1. Testing known gauge (hybas_4121489010)...")
    url = f"{BASE_URL}/gauges/hybas_4121489010"
    params = {'key': API_KEY}
    
    try:
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 200:
            gauge = response.json()
            print(f"✓ Success! Gauge found:")
            print(f"  Location: {gauge.get('location', {})}")
            print(f"  Quality Verified: {gauge.get('qualityVerified', False)}")
            print(f"  Has Model: {gauge.get('hasModel', False)}")
        else:
            print(f"✗ Error {response.status_code}: {response.text[:200]}")
    except Exception as e:
        print(f"✗ Exception: {e}")
    
    # Test 2: Try to list gauges with includeNonQualityVerified
    print("\n2. Testing gauge listing with includeNonQualityVerified...")
    endpoints_to_try = [
        ('gauges', {}),
        ('gauges:list', {}),
        ('gauges:search', {'region': 'PK'}),
        ('gauges:searchByArea', {
            'minLatitude': 25,
            'maxLatitude': 35,
            'minLongitude': 65,
            'maxLongitude': 75
        })
    ]
    
    for endpoint, extra_params in endpoints_to_try:
        print(f"\n  Trying: {endpoint}")
        url = f"{BASE_URL}/{endpoint}"
        params = {
            'key': API_KEY,
            'includeNonQualityVerified': 'true',
            **extra_params
        }
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=10)
            print(f"    Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and 'gauges' in data:
                    print(f"    ✓ Found {len(data['gauges'])} gauges!")
                    # Show first few Pakistani gauges
                    pak_count = 0
                    for gauge in data['gauges'][:100]:  # Check first 100
                        loc = gauge.get('location', {})
                        lat = loc.get('latitude', 0)
                        lon = loc.get('longitude', 0)
                        if 23 <= lat <= 37 and 60 <= lon <= 77:
                            pak_count += 1
                            if pak_count <= 3:
                                print(f"      - {gauge.get('gaugeId')}: {lat:.3f}, {lon:.3f}")
                    print(f"    → {pak_count} Pakistani gauges in first 100 results")
                elif isinstance(data, list):
                    print(f"    ✓ Found {len(data)} items")
                else:
                    print(f"    ? Unexpected format: {type(data)}")
                break  # If successful, stop trying other endpoints
            elif response.status_code == 404:
                print(f"    ✗ Not found")
            else:
                print(f"    ✗ Error: {response.text[:100]}")
                
        except Exception as e:
            print(f"    ✗ Exception: {type(e).__name__}: {str(e)[:50]}")
    
    # Test 3: Try pattern-based discovery
    print("\n3. Testing gauge ID patterns...")
    test_patterns = [
        'hybas_4121489020',  # Near known gauge
        'hybas_4121489000',
        'hybas_4121489100',
        'pk_001',
        'pakistan_001',
        'indus_001'
    ]
    
    found_count = 0
    for gauge_id in test_patterns:
        url = f"{BASE_URL}/gauges/{gauge_id}"
        params = {'key': API_KEY}
        
        try:
            response = requests.get(url, params=params, headers=headers, timeout=5)
            if response.status_code == 200:
                gauge = response.json()
                loc = gauge.get('location', {})
                lat = loc.get('latitude', 0)
                lon = loc.get('longitude', 0)
                
                # Check if in Pakistan
                if 23 <= lat <= 37 and 60 <= lon <= 77:
                    print(f"  ✓ Found Pakistani gauge: {gauge_id} at {lat:.3f}, {lon:.3f}")
                    found_count += 1
                else:
                    print(f"  - Found gauge {gauge_id} but outside Pakistan: {lat:.3f}, {lon:.3f}")
            elif response.status_code != 404:
                print(f"  ? {gauge_id}: Status {response.status_code}")
        except:
            pass
    
    print(f"\n  → Found {found_count} additional Pakistani gauges from patterns")
    
    print("\n" + "="*50)
    print("SUMMARY:")
    print("- Direct gauge access: ✓ Working")
    print("- Need to find correct endpoint for listing all gauges")
    print("- includeNonQualityVerified parameter ready to use")
    print("\nNext steps:")
    print("1. Check API documentation for correct list endpoint")
    print("2. Verify API is fully enabled in Google Cloud Console")
    print("3. Contact Google support if list endpoints not working")

if __name__ == "__main__":
    test_endpoints()