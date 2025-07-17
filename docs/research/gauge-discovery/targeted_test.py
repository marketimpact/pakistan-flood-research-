#!/usr/bin/env python3
"""
Targeted test focusing on high-probability ranges
"""

import os
import requests
import time
from datetime import datetime

def generate_targeted_ids():
    """Generate IDs in high-probability ranges based on known gauges"""
    
    # Known working gauges for pattern reference
    known_ranges = [
        # Around verified gauge
        (4121480000, 4121490000, 100),
        # Around Chitral gauge
        (4120560000, 4120580000, 100),
        # High-density areas from analysis
        (4120000000, 4120100000, 1000),
        (4120100000, 4120200000, 1000),
        (4120500000, 4120600000, 1000),
        (4120800000, 4120900000, 1000),
        (4120900000, 4121000000, 1000),
    ]
    
    gauge_ids = []
    
    for start, end, step in known_ranges:
        for i in range(start, end, step):
            gauge_ids.append(f"hybas_{i}")
    
    # Add some known working IDs to verify API
    gauge_ids.extend([
        "hybas_4121489010",  # Known verified
        "hybas_4120570410",  # Known Chitral
        "hybas_4120567890",  # Known working
    ])
    
    return gauge_ids

def test_gauge_batch(gauge_ids, api_key):
    """Test a batch of gauge IDs"""
    print(f"Testing {len(gauge_ids)} targeted gauge IDs...")
    
    base_url = 'https://floodforecasting.googleapis.com/v1'
    headers = {
        'X-goog-api-key': api_key,
        'Content-Type': 'application/json'
    }
    
    valid_gauges = []
    
    for i, gauge_id in enumerate(gauge_ids):
        try:
            gauge_url = f'{base_url}/gauges/{gauge_id}'
            response = requests.get(gauge_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                gauge_data = response.json()
                quality_verified = gauge_data.get('qualityVerified', False)
                status = "✓ VERIFIED" if quality_verified else "⚠ UNVERIFIED"
                location = gauge_data.get('location', {})
                
                print(f"[{i+1}/{len(gauge_ids)}] Found: {gauge_id} [{status}] "
                      f"({location.get('latitude', 'N/A')}, {location.get('longitude', 'N/A')})")
                
                valid_gauges.append({
                    'gauge_id': gauge_id,
                    'quality_verified': quality_verified,
                    'location': location,
                    'site_name': gauge_data.get('siteName', ''),
                    'river': gauge_data.get('river', ''),
                    'has_model': gauge_data.get('hasModel', False)
                })
            elif i % 50 == 0:
                print(f"[{i+1}/{len(gauge_ids)}] Tested {i+1} IDs, found {len(valid_gauges)} valid")
            
            # Rate limiting
            if i > 0 and i % 10 == 0:
                time.sleep(0.5)
                
        except Exception as e:
            print(f"[{i+1}/{len(gauge_ids)}] Error testing {gauge_id}: {e}")
            continue
    
    return valid_gauges

def main():
    # Get API key
    api_key = os.environ.get('GOOGLE_FLOOD_HUB_API_KEY')
    if not api_key:
        print("Error: GOOGLE_FLOOD_HUB_API_KEY not found in environment")
        return
    
    print("TARGETED GAUGE DISCOVERY TEST")
    print("=" * 50)
    print(f"Testing high-probability ranges...")
    print(f"Start time: {datetime.now()}")
    
    # Generate targeted IDs
    gauge_ids = generate_targeted_ids()
    
    # Test the gauges
    valid_gauges = test_gauge_batch(gauge_ids, api_key)
    
    # Summary
    print("\n" + "=" * 50)
    print("TARGETED TEST RESULTS")
    print("=" * 50)
    print(f"Total tested: {len(gauge_ids)}")
    print(f"Valid gauges found: {len(valid_gauges)}")
    print(f"Success rate: {len(valid_gauges)/len(gauge_ids)*100:.1f}%")
    
    if valid_gauges:
        verified_count = sum(1 for g in valid_gauges if g['quality_verified'])
        print(f"Quality verified: {verified_count}")
        print(f"Verification rate: {verified_count/len(valid_gauges)*100:.1f}%")
        
        print("\nValid gauges found:")
        for gauge in valid_gauges:
            status = "✓ VERIFIED" if gauge['quality_verified'] else "⚠ UNVERIFIED"
            print(f"  {gauge['gauge_id']} [{status}] - {gauge['site_name'] or 'Unnamed'}")
    
    print(f"\nEnd time: {datetime.now()}")

if __name__ == "__main__":
    main()