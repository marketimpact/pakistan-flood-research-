#!/usr/bin/env python3
"""
Quick test of our gauge discovery approach
Test first 100 IDs to validate methodology
"""

import os
import requests
import time
from datetime import datetime

def test_gauge_batch(gauge_ids, api_key):
    """Test a batch of gauge IDs"""
    print(f"Testing {len(gauge_ids)} gauge IDs...")
    
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
        print("Please set your API key:")
        print("export GOOGLE_FLOOD_HUB_API_KEY='your_api_key_here'")
        return
    
    # Load first 100 gauge IDs
    try:
        with open('gauge_ids_to_test.txt', 'r') as f:
            gauge_ids = [line.strip() for line in f][:100]
    except FileNotFoundError:
        print("gauge_ids_to_test.txt not found. Run systematic_gauge_discovery.py first.")
        return
    
    print("QUICK GAUGE DISCOVERY TEST")
    print("=" * 50)
    print(f"Testing first 100 systematically generated IDs...")
    print(f"Start time: {datetime.now()}")
    
    # Test the gauges
    valid_gauges = test_gauge_batch(gauge_ids, api_key)
    
    # Summary
    print("\n" + "=" * 50)
    print("QUICK TEST RESULTS")
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
    print("\nNext steps:")
    print("1. Run full test with test_gauge_ids.py for all 5,000 candidates")
    print("2. Update Django database with discovered gauges")
    print("3. Run multiple discovery iterations to find more gauges")

if __name__ == "__main__":
    main()