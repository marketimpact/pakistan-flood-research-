#!/usr/bin/env python3
"""
Systematic search for Pakistani gauges by testing gauge ID patterns
Since list/search endpoints don't work, we'll discover gauges by ID
"""

import requests
import json
import time
import csv
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

API_KEY = "AIzaSyB0d7jLuqXjDJW_BQxOyCrBVt97zse7S-M"
BASE_URL = "https://floodforecasting.googleapis.com/v1"

# Pakistan bounds
PAK_BOUNDS = {
    'min_lat': 23.0, 'max_lat': 37.0,
    'min_lon': 60.0, 'max_lon': 77.0
}

def check_gauge(gauge_id):
    """Check if a gauge ID exists and is in Pakistan"""
    url = f"{BASE_URL}/gauges/{gauge_id}"
    params = {'key': API_KEY}
    headers = {'X-goog-api-key': API_KEY}
    
    try:
        response = requests.get(url, params=params, headers=headers, timeout=5)
        if response.status_code == 200:
            gauge = response.json()
            loc = gauge.get('location', {})
            lat = loc.get('latitude', 0)
            lon = loc.get('longitude', 0)
            
            # Check if in Pakistan
            if (PAK_BOUNDS['min_lat'] <= lat <= PAK_BOUNDS['max_lat'] and 
                PAK_BOUNDS['min_lon'] <= lon <= PAK_BOUNDS['max_lon']):
                return gauge
    except:
        pass
    
    return None

def generate_gauge_ids():
    """Generate potential gauge IDs to test"""
    gauge_ids = []
    
    # HYBAS patterns - based on known gauge hybas_4121489010
    # Try ranges around the known gauge
    for base in [4121489, 4121488, 4121490, 4121487, 4121491]:
        for suffix in range(0, 200, 10):  # Every 10th to start
            gauge_ids.append(f'hybas_{base}{suffix:03d}')
    
    # Try other HYBAS patterns that might be in Pakistan region
    # South Asian region codes
    for base in [412, 413, 414, 415, 611, 612, 613]:
        for mid in range(1000, 2000, 100):
            for suffix in range(0, 100, 20):
                gauge_ids.append(f'hybas_{base}{mid}{suffix:03d}')
    
    # Country/region specific patterns
    patterns = [
        'pk', 'PK', 'pakistan', 'Pakistan', 'PAK',
        'indus', 'Indus', 'jhelum', 'chenab', 'ravi', 'sutlej',
        'sind', 'sindh', 'punjab', 'balochistan', 'kpk', 'gb'
    ]
    
    for pattern in patterns:
        for num in range(1, 200):
            gauge_ids.extend([
                f'{pattern}_{num:03d}',
                f'{pattern}_{num:04d}',
                f'{pattern}{num:03d}',
                f'{pattern}-{num:03d}'
            ])
    
    # Agency patterns
    agencies = ['pmd', 'PMD', 'wapda', 'WAPDA', 'suparco', 'SUPARCO']
    for agency in agencies:
        for num in range(1, 100):
            gauge_ids.extend([
                f'{agency}_{num:03d}',
                f'{agency}{num:03d}',
                f'{agency}_pk_{num:03d}'
            ])
    
    # Remove duplicates
    return list(set(gauge_ids))

def search_gauges_parallel(gauge_ids, max_workers=5):
    """Search for gauges in parallel with rate limiting"""
    found_gauges = []
    
    print(f"🔍 Testing {len(gauge_ids)} potential gauge IDs...")
    print("This may take several minutes. Progress will be shown every 100 checks.")
    
    checked = 0
    found_in_pak = 0
    found_outside = 0
    
    # Process in batches to manage rate limits
    batch_size = 100
    
    for i in range(0, len(gauge_ids), batch_size):
        batch = gauge_ids[i:i+batch_size]
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_id = {executor.submit(check_gauge, gid): gid for gid in batch}
            
            for future in as_completed(future_to_id):
                gauge_id = future_to_id[future]
                checked += 1
                
                try:
                    result = future.result()
                    if result:
                        found_gauges.append(result)
                        found_in_pak += 1
                        print(f"  ✓ Found Pakistani gauge: {gauge_id}")
                except:
                    pass
                
                # Progress update
                if checked % 100 == 0:
                    print(f"  Progress: {checked}/{len(gauge_ids)} checked, "
                          f"{found_in_pak} Pakistani gauges found")
        
        # Rate limiting between batches
        time.sleep(2)
    
    return found_gauges

def analyze_results(gauges):
    """Analyze discovered gauges"""
    if not gauges:
        print("\n❌ No Pakistani gauges found")
        return
    
    print(f"\n📊 FOUND {len(gauges)} PAKISTANI GAUGES")
    print("="*60)
    
    # Statistics
    verified = sum(1 for g in gauges if g.get('qualityVerified', False))
    has_model = sum(1 for g in gauges if g.get('hasModel', False))
    both = sum(1 for g in gauges if g.get('qualityVerified', False) and g.get('hasModel', False))
    
    print(f"✅ Quality Verified: {verified} ({verified/len(gauges)*100:.1f}%)")
    print(f"📈 Has Model: {has_model} ({has_model/len(gauges)*100:.1f}%)")
    print(f"⭐ Both Verified + Model: {both} ({both/len(gauges)*100:.1f}%)")
    
    # Group by source
    sources = {}
    for gauge in gauges:
        source = gauge.get('source', 'Unknown')
        sources[source] = sources.get(source, 0) + 1
    
    print("\n📍 Sources:")
    for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
        print(f"  {source}: {count}")
    
    # Show sample gauge IDs
    print("\n🏷️ Sample Gauge IDs:")
    for gauge in gauges[:10]:
        loc = gauge.get('location', {})
        print(f"  {gauge.get('gaugeId')}: {loc.get('latitude'):.3f}, {loc.get('longitude'):.3f} "
              f"({'Verified' if gauge.get('qualityVerified') else 'Unverified'})")
    
    if len(gauges) > 10:
        print(f"  ... and {len(gauges) - 10} more")

def export_results(gauges):
    """Export discovered gauges to CSV"""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'pakistan_gauges_discovered_{timestamp}.csv'
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'gauge_id', 'latitude', 'longitude', 'river', 'site_name',
            'quality_verified', 'has_model', 'source', 'discovery_method'
        ])
        
        writer.writeheader()
        for gauge in gauges:
            loc = gauge.get('location', {})
            writer.writerow({
                'gauge_id': gauge.get('gaugeId', ''),
                'latitude': loc.get('latitude', ''),
                'longitude': loc.get('longitude', ''),
                'river': gauge.get('river', ''),
                'site_name': gauge.get('siteName', ''),
                'quality_verified': gauge.get('qualityVerified', False),
                'has_model': gauge.get('hasModel', False),
                'source': gauge.get('source', ''),
                'discovery_method': 'Systematic ID search'
            })
    
    print(f"\n💾 Exported to {filename}")
    
    # Also save raw JSON
    json_filename = f'pakistan_gauges_raw_{timestamp}.json'
    with open(json_filename, 'w') as f:
        json.dump(gauges, f, indent=2)
    
    print(f"📄 Raw data saved to {json_filename}")

def main():
    """Main execution"""
    print("🚀 SYSTEMATIC PAKISTANI GAUGE DISCOVERY")
    print(f"Started: {datetime.now().isoformat()}")
    print("="*60)
    
    # Generate gauge IDs to test
    print("1️⃣ Generating potential gauge IDs...")
    gauge_ids = generate_gauge_ids()
    print(f"   Generated {len(gauge_ids)} IDs to test")
    
    # Limit for initial testing (remove this for full search)
    print("\n⚠️  Limiting to first 1000 IDs for initial test")
    gauge_ids = gauge_ids[:1000]
    
    # Search for gauges
    print("\n2️⃣ Searching for Pakistani gauges...")
    found_gauges = search_gauges_parallel(gauge_ids, max_workers=3)
    
    # Analyze results
    print("\n3️⃣ Analyzing results...")
    analyze_results(found_gauges)
    
    # Export results
    if found_gauges:
        export_results(found_gauges)
    
    print("\n✅ SEARCH COMPLETE")
    print("="*60)
    
    if len(found_gauges) < 50:
        print("\n💡 To find more gauges:")
        print("  1. Remove the 1000 ID limit in the script")
        print("  2. Add more ID patterns based on found gauges")
        print("  3. Check Google Flood Hub website for gauge examples")
        print("  4. Contact Google support for bulk access methods")

if __name__ == "__main__":
    main()