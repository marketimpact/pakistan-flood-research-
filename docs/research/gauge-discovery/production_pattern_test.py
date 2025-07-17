#!/usr/bin/env python3
"""
Test gauge IDs using the exact patterns from production discoveries
"""

import os
import requests
import time
import random
from datetime import datetime

def generate_production_pattern_ids():
    """Generate IDs based on the exact production patterns that worked"""
    
    # The 28 gauges found in production (excluding known ones)
    production_gauges = [
        "hybas_4121489010",  # Quality verified
        "hybas_4120570410",  # Chitral
        "hybas_4120567890",
        "hybas_4120983530",
        "hybas_4120857010",
        "hybas_4120962950",
        "hybas_4120573410",
        "hybas_4120915890",
        "hybas_4120121470",
        "hybas_4120760570",
        "hybas_4120558140",
        "hybas_4120210000",
        "hybas_4120124220",
        "hybas_4120492590",
        "hybas_4120038810",
        "hybas_4120115500",
        "hybas_4120092960",
        "hybas_4120954970",
        "hybas_4120890520",
        "hybas_4120127960",
        "hybas_4120502440",
        "hybas_4120449360",
        "hybas_4120604970",
        "hybas_4120073530",
        "hybas_4120031450",
        "hybas_4120873950",
        "hybas_4120825520",
        "hybas_4120476650",
    ]
    
    gauge_ids = []
    
    # Extract the numeric patterns from known working gauges
    working_numbers = []
    for gauge in production_gauges:
        num = int(gauge.split('_')[1])
        working_numbers.append(num)
    
    # Generate variations around known working patterns
    for base_num in working_numbers:
        # Try variations around each known working gauge
        for offset in [-100, -50, -20, -10, -5, -2, -1, 1, 2, 5, 10, 20, 50, 100]:
            new_num = base_num + offset
            if 4120000000 <= new_num <= 4129999999:
                gauge_ids.append(f"hybas_{new_num}")
    
    # Also use the systematic ranges that the production system used
    # The production system used random generation in these ranges:
    id_ranges = [
        (4120000000, 4120999999),  # General Pakistan range
        (4121000000, 4121999999),  # Extended range
        (4122000000, 4122999999),  # Additional range
    ]
    
    # Generate some random IDs in these ranges (like production did)
    for start, end in id_ranges:
        for _ in range(100):  # 100 per range
            gauge_num = random.randint(start, end)
            gauge_ids.append(f"hybas_{gauge_num}")
    
    return list(set(gauge_ids))  # Remove duplicates

def test_gauge_batch(gauge_ids, api_key, max_test=500):
    """Test a batch of gauge IDs with better progress reporting"""
    print(f"Testing {min(len(gauge_ids), max_test)} gauge IDs...")
    
    base_url = 'https://floodforecasting.googleapis.com/v1'
    headers = {
        'X-goog-api-key': api_key,
        'Content-Type': 'application/json'
    }
    
    valid_gauges = []
    test_ids = gauge_ids[:max_test]  # Limit for testing
    
    for i, gauge_id in enumerate(test_ids):
        try:
            gauge_url = f'{base_url}/gauges/{gauge_id}'
            response = requests.get(gauge_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                gauge_data = response.json()
                quality_verified = gauge_data.get('qualityVerified', False)
                status = "✓ VERIFIED" if quality_verified else "⚠ UNVERIFIED"
                location = gauge_data.get('location', {})
                
                print(f"[{i+1}/{len(test_ids)}] Found: {gauge_id} [{status}]")
                
                valid_gauges.append({
                    'gauge_id': gauge_id,
                    'quality_verified': quality_verified,
                    'location': location,
                    'site_name': gauge_data.get('siteName', ''),
                    'river': gauge_data.get('river', ''),
                    'has_model': gauge_data.get('hasModel', False)
                })
            
            # Progress reporting
            if i % 50 == 0 and i > 0:
                print(f"[{i+1}/{len(test_ids)}] Progress: {i+1} tested, {len(valid_gauges)} valid found")
            
            # Rate limiting
            if i > 0 and i % 10 == 0:
                time.sleep(0.3)
                
        except Exception as e:
            if i % 100 == 0:
                print(f"[{i+1}/{len(test_ids)}] Some errors occurred (normal for 404s)")
            continue
    
    return valid_gauges

def main():
    # Get API key
    api_key = os.environ.get('GOOGLE_FLOOD_HUB_API_KEY')
    if not api_key:
        print("Error: GOOGLE_FLOOD_HUB_API_KEY not found in environment")
        return
    
    print("PRODUCTION PATTERN GAUGE DISCOVERY")
    print("=" * 50)
    print(f"Testing patterns from production discoveries...")
    print(f"Start time: {datetime.now()}")
    
    # Generate IDs based on production patterns
    gauge_ids = generate_production_pattern_ids()
    print(f"Generated {len(gauge_ids)} candidate IDs")
    
    # Test the gauges
    valid_gauges = test_gauge_batch(gauge_ids, api_key, max_test=500)
    
    # Summary
    print("\n" + "=" * 50)
    print("PRODUCTION PATTERN TEST RESULTS")
    print("=" * 50)
    print(f"Total tested: {min(len(gauge_ids), 500)}")
    print(f"Valid gauges found: {len(valid_gauges)}")
    print(f"Success rate: {len(valid_gauges)/min(len(gauge_ids), 500)*100:.1f}%")
    
    if valid_gauges:
        verified_count = sum(1 for g in valid_gauges if g['quality_verified'])
        print(f"Quality verified: {verified_count}")
        print(f"Verification rate: {verified_count/len(valid_gauges)*100:.1f}%")
        
        print("\nValid gauges found:")
        for gauge in valid_gauges:
            status = "✓ VERIFIED" if gauge['quality_verified'] else "⚠ UNVERIFIED"
            print(f"  {gauge['gauge_id']} [{status}] - {gauge['site_name'] or 'Unnamed'}")
            
        # Export new discoveries
        new_gauges = [g['gauge_id'] for g in valid_gauges]
        with open('newly_discovered_gauges.txt', 'w') as f:
            for gauge_id in new_gauges:
                f.write(f"{gauge_id}\n")
        print(f"\nNew discoveries saved to newly_discovered_gauges.txt")
    
    print(f"\nEnd time: {datetime.now()}")

if __name__ == "__main__":
    main()