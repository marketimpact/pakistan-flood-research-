#!/usr/bin/env python3
"""
Massive Pakistani Gauge Discovery
Aggressively search for all Pakistani gauges using proven patterns
"""

import requests
import json
import time
import csv
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import os

API_KEY = "AIzaSyB0d7jLuqXjDJW_BQxOyCrBVt97zse7S-M"
BASE_URL = "https://floodforecasting.googleapis.com/v1"

# Pakistan bounds
PAK_BOUNDS = {
    'min_lat': 23.0, 'max_lat': 37.0,
    'min_lon': 60.0, 'max_lon': 77.0
}

class GaugeDiscovery:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({'X-goog-api-key': API_KEY})
        self.found_gauges = []
        self.checked_count = 0
        self.start_time = time.time()
        
    def check_gauge(self, gauge_id):
        """Check if gauge exists and is in Pakistan"""
        url = f"{BASE_URL}/gauges/{gauge_id}"
        params = {'key': API_KEY}
        
        try:
            response = self.session.get(url, params=params, timeout=3)
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
    
    def test_batch(self, base, start, end):
        """Test a batch of gauge IDs"""
        found = []
        for i in range(start, end):
            gauge_id = f'hybas_{base}{i:04d}'
            result = self.check_gauge(gauge_id)
            if result:
                found.append(result)
                print(f"✓ Found: {gauge_id} - {result.get('qualityVerified', False) and 'Verified' or 'Unverified'}")
        return found
    
    def discover_gauges(self):
        """Main discovery process"""
        print("🚀 MASSIVE PAKISTANI GAUGE DISCOVERY")
        print("="*60)
        print(f"Started: {datetime.now()}")
        print(f"Target: Test 30,000+ gauge IDs")
        print(f"Expected: 50-100+ Pakistani gauges")
        print("="*60)
        
        # Priority patterns based on confirmed gauges
        priority_bases = [
            '412149',  # Confirmed pattern (2 gauges found)
            '412148',  # Adjacent
            '412150',  # Adjacent
            '412147',  
            '412151',
            '412146',
            '412152'
        ]
        
        # Extended search patterns
        extended_bases = [
            '412140', '412141', '412142', '412143', '412144', '412145',
            '412153', '412154', '412155', '412156', '412157', '412158',
            '413148', '413149', '413150',  # Adjacent regions
            '411148', '411149', '411150',  # Western regions
            '421148', '421149', '421150'   # Eastern regions
        ]
        
        all_results = []
        
        # Phase 1: Priority search
        print("\n📍 PHASE 1: Priority Pattern Search")
        print("-"*40)
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            
            for base in priority_bases:
                print(f"Queuing base pattern: hybas_{base}xxxx")
                # Test in chunks of 100
                for start in range(0, 2000, 100):  # First 2000 of each priority base
                    future = executor.submit(self.test_batch, base, start, start + 100)
                    futures.append(future)
            
            # Process results
            completed = 0
            for future in as_completed(futures):
                completed += 1
                results = future.result()
                all_results.extend(results)
                
                if completed % 10 == 0:
                    elapsed = time.time() - self.start_time
                    rate = completed * 100 / elapsed
                    print(f"Progress: {completed * 100} IDs checked | Found: {len(all_results)} | Rate: {rate:.0f} IDs/sec")
        
        # Phase 2: Extended search (if needed)
        if len(all_results) < 50:
            print(f"\n📍 PHASE 2: Extended Pattern Search")
            print("-"*40)
            print(f"Found {len(all_results)} gauges so far, extending search...")
            
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = []
                
                for base in extended_bases[:5]:  # First 5 extended patterns
                    print(f"Queuing extended pattern: hybas_{base}xxxx")
                    for start in range(0, 1000, 100):  # First 1000 of each
                        future = executor.submit(self.test_batch, base, start, start + 100)
                        futures.append(future)
                
                for future in as_completed(futures):
                    results = future.result()
                    all_results.extend(results)
        
        return all_results
    
    def analyze_and_export(self, gauges):
        """Analyze and export results"""
        if not gauges:
            print("\n❌ No gauges found!")
            return
        
        print(f"\n📊 DISCOVERY RESULTS")
        print("="*60)
        print(f"Total Pakistani Gauges Found: {len(gauges)}")
        
        # Remove duplicates
        unique_gauges = {}
        for gauge in gauges:
            gauge_id = gauge.get('gaugeId')
            if gauge_id and gauge_id not in unique_gauges:
                unique_gauges[gauge_id] = gauge
        
        gauges = list(unique_gauges.values())
        print(f"Unique Gauges: {len(gauges)}")
        
        # Analysis
        verified = sum(1 for g in gauges if g.get('qualityVerified', False))
        has_model = sum(1 for g in gauges if g.get('hasModel', False))
        
        print(f"\n📈 Quality Analysis:")
        print(f"  Quality Verified: {verified} ({verified/len(gauges)*100:.1f}%)")
        print(f"  Has Model: {has_model} ({has_model/len(gauges)*100:.1f}%)")
        print(f"  High Priority (Verified + Model): {sum(1 for g in gauges if g.get('qualityVerified') and g.get('hasModel'))}")
        
        # Geographic distribution
        print(f"\n🗺️ Geographic Distribution:")
        lat_ranges = {
            'South (23-27°N)': 0,
            'Central (27-31°N)': 0,
            'North (31-35°N)': 0,
            'Far North (35-37°N)': 0
        }
        
        for gauge in gauges:
            lat = gauge.get('location', {}).get('latitude', 0)
            if 23 <= lat < 27:
                lat_ranges['South (23-27°N)'] += 1
            elif 27 <= lat < 31:
                lat_ranges['Central (27-31°N)'] += 1
            elif 31 <= lat < 35:
                lat_ranges['North (31-35°N)'] += 1
            elif 35 <= lat <= 37:
                lat_ranges['Far North (35-37°N)'] += 1
        
        for region, count in lat_ranges.items():
            print(f"  {region}: {count} gauges")
        
        # Export comprehensive CSV
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        csv_filename = f'pakistan_gauges_comprehensive_{timestamp}.csv'
        
        with open(csv_filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'gauge_id', 'latitude', 'longitude', 'river', 'site_name',
                'quality_verified', 'has_model', 'source', 'priority_level',
                'region', 'discovery_timestamp'
            ])
            
            writer.writeheader()
            for gauge in gauges:
                loc = gauge.get('location', {})
                lat = loc.get('latitude', 0)
                lon = loc.get('longitude', 0)
                
                # Determine priority
                if gauge.get('qualityVerified') and gauge.get('hasModel'):
                    priority = 'HIGH'
                elif gauge.get('qualityVerified') or gauge.get('hasModel'):
                    priority = 'MEDIUM'
                else:
                    priority = 'LOW'
                
                # Determine region
                if lat >= 35:
                    region = 'Far North'
                elif lat >= 31:
                    region = 'North'
                elif lat >= 27:
                    region = 'Central'
                else:
                    region = 'South'
                
                writer.writerow({
                    'gauge_id': gauge.get('gaugeId', ''),
                    'latitude': lat,
                    'longitude': lon,
                    'river': gauge.get('river', ''),
                    'site_name': gauge.get('siteName', ''),
                    'quality_verified': gauge.get('qualityVerified', False),
                    'has_model': gauge.get('hasModel', False),
                    'source': gauge.get('source', ''),
                    'priority_level': priority,
                    'region': region,
                    'discovery_timestamp': datetime.now().isoformat()
                })
        
        print(f"\n💾 Exported to: {csv_filename}")
        
        # Export JSON with full details
        json_filename = f'pakistan_gauges_full_{timestamp}.json'
        with open(json_filename, 'w') as f:
            json.dump({
                'discovery_metadata': {
                    'timestamp': datetime.now().isoformat(),
                    'total_found': len(gauges),
                    'quality_verified': verified,
                    'has_model': has_model,
                    'api_key_used': 'Valid',
                    'method': 'Systematic HYBAS pattern search'
                },
                'gauges': gauges
            }, f, indent=2)
        
        print(f"📄 Full data exported to: {json_filename}")
        
        # Show sample high-priority gauges
        print(f"\n⭐ Sample HIGH PRIORITY Gauges:")
        high_priority = [g for g in gauges if g.get('qualityVerified') and g.get('hasModel')]
        for gauge in high_priority[:5]:
            loc = gauge.get('location', {})
            print(f"  {gauge.get('gaugeId')}: {loc.get('latitude'):.3f}, {loc.get('longitude'):.3f}")
        
        if len(high_priority) > 5:
            print(f"  ... and {len(high_priority) - 5} more high priority gauges")
        
        return gauges

def main():
    """Execute massive discovery"""
    discovery = GaugeDiscovery()
    
    try:
        # Discover gauges
        all_gauges = discovery.discover_gauges()
        
        # Analyze and export
        discovery.analyze_and_export(all_gauges)
        
        # Final summary
        elapsed = time.time() - discovery.start_time
        print(f"\n✅ DISCOVERY COMPLETE")
        print(f"Total time: {elapsed/60:.1f} minutes")
        print(f"Gauges discovered: {len(all_gauges)}")
        
        if len(all_gauges) >= 50:
            print(f"\n🎉 SUCCESS! Found substantial Pakistani gauge network!")
        elif len(all_gauges) >= 10:
            print(f"\n✓ Good progress! Found multiple gauges for monitoring.")
        else:
            print(f"\n⚠️ Limited gauges found. Consider expanding search patterns.")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ Discovery interrupted by user")
        print(f"Partial results: {len(discovery.found_gauges)} gauges found")
        
    except Exception as e:
        print(f"\n❌ Error during discovery: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()