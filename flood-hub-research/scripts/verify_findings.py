#!/usr/bin/env python3
"""
Verify the real data findings - double check API responses
"""

import json
import urllib.request
import urllib.parse
from datetime import datetime

# Configuration
API_KEY = "AIzaSyB0d7jLuqXjDJW_BQxOyCrBVt97zse7S-M"
BASE_URL = "https://floodforecasting.googleapis.com/v1"

def make_api_request(endpoint, params=None):
    """Make API request using urllib"""
    url = f"{BASE_URL}/{endpoint}"
    
    if params is None:
        params = {}
    params['key'] = API_KEY
    
    headers = {'X-goog-api-key': API_KEY}
    query_string = urllib.parse.urlencode(params)
    full_url = f"{url}?{query_string}"
    
    request = urllib.request.Request(full_url, headers=headers)
    
    try:
        with urllib.request.urlopen(request) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        return {"error": str(e)}

print("🔍 VERIFYING GOOGLE FLOOD HUB FINDINGS")
print("="*60)

# Test 1: Check the claimed gauge hybas_4121489010
print("\n1. Testing gauge hybas_4121489010 (from real_data_findings.md):")
gauge_info = make_api_request("gauges/hybas_4121489010")
if "error" not in gauge_info:
    print(f"   ✓ Gauge exists!")
    print(f"   Location: {gauge_info.get('location', {})}")
    print(f"   Quality Verified: {gauge_info.get('qualityVerified')}")
    print(f"   Has Model: {gauge_info.get('hasModel')}")
else:
    print(f"   ✗ Error: {gauge_info['error']}")

# Get model data
print("\n2. Getting threshold data:")
model_info = make_api_request("gaugeModels/hybas_4121489010")
if "error" not in model_info:
    thresholds = model_info.get('thresholds', {})
    print(f"   Warning: {thresholds.get('warningLevel')} m³/s")
    print(f"   Danger: {thresholds.get('dangerLevel')} m³/s")
    print(f"   Extreme: {thresholds.get('extremeDangerLevel')} m³/s")
else:
    print(f"   ✗ Error: {model_info['error']}")

# Test 2: Re-check Chitral gauge hybas_4120570410
print("\n3. Re-checking Chitral gauge hybas_4120570410:")
chitral_info = make_api_request("gauges/hybas_4120570410")
if "error" not in chitral_info:
    print(f"   ✓ Gauge exists!")
    print(f"   Location: {chitral_info.get('location', {})}")
    print(f"   Quality Verified: {chitral_info.get('qualityVerified')}")
    print(f"   Has Model: {chitral_info.get('hasModel')}")
else:
    print(f"   ✗ Error: {chitral_info['error']}")

# Test 3: Try to list gauges
print("\n4. Testing gauge listing endpoints:")
endpoints = ["gauges", "gauges:list", "gauges:search"]
for endpoint in endpoints:
    print(f"   Trying {endpoint}...", end="")
    result = make_api_request(endpoint)
    if "error" not in result:
        print(f" SUCCESS! Found data")
        if isinstance(result, list):
            print(f"   → {len(result)} items")
        elif isinstance(result, dict):
            print(f"   → Keys: {list(result.keys())}")
    else:
        print(f" Failed: {result['error'][:50]}...")

# Test 4: Check flood status
print("\n5. Testing flood status endpoints:")
for gauge_id in ["hybas_4121489010", "hybas_4120570410"]:
    print(f"   Gauge {gauge_id}:", end="")
    status = make_api_request("floodStatus", {"gaugeId": gauge_id})
    if "error" not in status:
        print(" HAS FLOOD STATUS!")
        if isinstance(status, list) and status:
            print(f"     Severity: {status[0].get('severity', 'N/A')}")
        elif isinstance(status, dict):
            print(f"     Data keys: {list(status.keys())}")
    else:
        print(f" No status: {status['error'][:30]}...")

print("\n" + "="*60)
print("VERIFICATION COMPLETE")