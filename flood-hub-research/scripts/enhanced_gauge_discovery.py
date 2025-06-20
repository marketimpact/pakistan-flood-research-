#!/usr/bin/env python3
"""
Enhanced Pakistani Gauge Discovery
Uses all available parameters including includeNonQualityVerified
"""

import json
import urllib.request
import urllib.parse
import urllib.error
from datetime import datetime
import csv
import time
import ssl

# Configuration
API_KEY = "AIzaSyB0d7jLuqXjDJW_BQxOyCrBVt97zse7S-M"
BASE_URL = "https://floodforecasting.googleapis.com/v1"

# Pakistan bounding box
PAKISTAN_BOUNDS = {
    'min_lat': 23.0,
    'max_lat': 37.0,
    'min_lon': 60.0,
    'max_lon': 77.0
}

# Create SSL context to handle certificates
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

def make_api_request(endpoint, params=None, method='GET'):
    """Make API request with enhanced error handling"""
    url = f"{BASE_URL}/{endpoint}"
    
    if params is None:
        params = {}
    
    # Always include API key
    params['key'] = API_KEY
    
    # CRITICAL: Include non-quality verified gauges
    if 'includeNonQualityVerified' not in params:
        params['includeNonQualityVerified'] = 'true'
    
    # Build URL with parameters
    query_string = urllib.parse.urlencode(params)
    full_url = f"{url}?{query_string}"
    
    # Create request with headers
    headers = {
        'X-goog-api-key': API_KEY,
        'Accept': 'application/json',
        'User-Agent': 'PakistanFloodResearch/1.0'
    }
    
    request = urllib.request.Request(full_url, headers=headers, method=method)
    
    print(f"→ Requesting: {endpoint}")
    print(f"  Parameters: {params}")
    
    try:
        with urllib.request.urlopen(request, context=ssl_context) as response:
            data = json.loads(response.read().decode())
            return data
    except urllib.error.HTTPError as e:
        print(f"  HTTP Error {e.code}: {e.reason}")
        if e.code == 403:
            print("  Note: 403 may indicate API needs to be enabled in Google Cloud Console")
        elif e.code == 404:
            print("  Note: 404 may indicate incorrect endpoint or missing resources")
        try:
            error_content = e.read().decode()
            error_json = json.loads(error_content)
            print(f"  Error details: {error_json.get('error', {}).get('message', 'No details')}")
        except:
            pass
        return None
    except Exception as e:
        print(f"  Error: {type(e).__name__}: {e}")
        return None

def try_direct_gauge_queries():
    """Try querying known gauge patterns directly"""
    print("\n🔍 TRYING DIRECT GAUGE QUERIES")
    print("="*60)
    
    found_gauges = []
    
    # Known gauge from previous discovery
    known_gauges = ['hybas_4121489010']
    
    # Generate potential gauge IDs
    potential_patterns = [
        # HYBAS patterns (sequential around known gauge)
        [f'hybas_412148{i:04d}' for i in range(9000, 9100)],
        [f'hybas_612011{i:04d}' for i in range(1520, 1560)],
        # Pakistan-specific patterns
        [f'pk_{i:03d}' for i in range(1, 100)],
        [f'PK_{i:03d}' for i in range(1, 100)],
        [f'pakistan_{i:03d}' for i in range(1, 50)],
        # Agency patterns
        [f'pmd_{i:03d}' for i in range(1, 50)],
        [f'wapda_{i:03d}' for i in range(1, 50)],
        # River patterns
        [f'indus_{i:03d}' for i in range(1, 50)],
        [f'jhelum_{i:03d}' for i in range(1, 30)],
        [f'chenab_{i:03d}' for i in range(1, 30)],
    ]
    
    # Test known gauges first
    for gauge_id in known_gauges:
        response = make_api_request(f'gauges/{gauge_id}')
        if response:
            print(f"  ✓ Found: {gauge_id}")
            found_gauges.append(response)
            time.sleep(0.1)  # Rate limiting
    
    # Test patterns (limited to avoid rate limits)
    tested = 0
    max_tests = 50  # Limit initial testing
    
    for pattern_list in potential_patterns:
        for gauge_id in pattern_list[:5]:  # Test first 5 of each pattern
            if tested >= max_tests:
                break
            
            response = make_api_request(f'gauges/{gauge_id}')
            if response:
                print(f"  ✓ Found: {gauge_id}")
                found_gauges.append(response)
                
                # If we find one, test nearby IDs
                base = gauge_id[:-3]
                for i in range(-5, 6):
                    try:
                        nearby_id = f"{base}{int(gauge_id[-3:]) + i:03d}"
                        nearby_response = make_api_request(f'gauges/{nearby_id}')
                        if nearby_response:
                            print(f"    ✓ Also found: {nearby_id}")
                            found_gauges.append(nearby_response)
                    except:
                        pass
            
            tested += 1
            time.sleep(0.3)  # Rate limiting
    
    return found_gauges

def try_batch_get():
    """Try batch get with multiple gauge IDs"""
    print("\n🔍 TRYING BATCH GET")
    print("="*60)
    
    # Try batchGet endpoint with known patterns
    gauge_names = [
        'gauges/hybas_4121489010',
        'gauges/hybas_4121489020',
        'gauges/hybas_4121489030',
        'gauges/hybas_6120111530',
        'gauges/pk_001',
        'gauges/pakistan_001',
        'gauges/indus_001'
    ]
    
    params = {
        'names': gauge_names,
        'includeNonQualityVerified': 'true'
    }
    
    response = make_api_request('gauges:batchGet', params)
    if response:
        return response.get('gauges', [])
    
    return []

def search_by_grid():
    """Search Pakistan in grid cells"""
    print("\n🔍 GRID-BASED SEARCH")
    print("="*60)
    
    all_gauges = []
    
    # Try smaller grid cells (2x2 degrees)
    grid_size = 2
    
    for lat in range(23, 37, grid_size):
        for lon in range(60, 77, grid_size):
            print(f"\n  Searching grid: {lat}-{lat+grid_size}°N, {lon}-{lon+grid_size}°E")
            
            # Try different parameter formats
            param_variations = [
                {
                    'minLatitude': lat,
                    'maxLatitude': lat + grid_size,
                    'minLongitude': lon,
                    'maxLongitude': lon + grid_size,
                    'includeNonQualityVerified': 'true'
                },
                {
                    'bounds': f"{lat},{lon},{lat+grid_size},{lon+grid_size}",
                    'includeNonQualityVerified': 'true'
                },
                {
                    'bbox': f"{lon},{lat},{lon+grid_size},{lat+grid_size}",
                    'includeNonQualityVerified': 'true'
                }
            ]
            
            for params in param_variations:
                for endpoint in ['gauges', 'gauges:search', 'gauges:searchByArea']:
                    response = make_api_request(endpoint, params)
                    if response:
                        if isinstance(response, dict) and 'gauges' in response:
                            gauges = response['gauges']
                        elif isinstance(response, list):
                            gauges = response
                        else:
                            continue
                        
                        # Filter for Pakistan bounds
                        for gauge in gauges:
                            loc = gauge.get('location', {})
                            g_lat = loc.get('latitude', 0)
                            g_lon = loc.get('longitude', 0)
                            
                            if (PAKISTAN_BOUNDS['min_lat'] <= g_lat <= PAKISTAN_BOUNDS['max_lat'] and
                                PAKISTAN_BOUNDS['min_lon'] <= g_lon <= PAKISTAN_BOUNDS['max_lon']):
                                all_gauges.append(gauge)
                        
                        if gauges:
                            print(f"    ✓ Found {len(gauges)} gauges with {endpoint}")
                            # If one format works, skip others
                            return all_gauges
                    
                    time.sleep(0.2)  # Rate limiting
    
    return all_gauges

def analyze_and_export_gauges(all_gauges):
    """Analyze and export discovered gauges"""
    if not all_gauges:
        print("\n❌ No gauges discovered")
        return
    
    # Remove duplicates
    unique_gauges = {}
    for gauge in all_gauges:
        gauge_id = gauge.get('gaugeId', '')
        if gauge_id and gauge_id not in unique_gauges:
            unique_gauges[gauge_id] = gauge
    
    gauges = list(unique_gauges.values())
    
    print(f"\n📊 ANALYSIS OF {len(gauges)} UNIQUE PAKISTANI GAUGES")
    print("="*60)
    
    # Statistics
    quality_verified = sum(1 for g in gauges if g.get('qualityVerified', False))
    has_model = sum(1 for g in gauges if g.get('hasModel', False))
    
    print(f"\n✅ Quality Verified: {quality_verified}/{len(gauges)} ({quality_verified/len(gauges)*100:.1f}%)")
    print(f"📈 Has Model: {has_model}/{len(gauges)} ({has_model/len(gauges)*100:.1f}%)")
    
    # Export to CSV
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_filename = f"pakistan_gauges_enhanced_{timestamp}.csv"
    
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['gauge_id', 'latitude', 'longitude', 'river', 'site_name', 
                     'quality_verified', 'has_model', 'source', 'confidence_level']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for gauge in gauges:
            loc = gauge.get('location', {})
            
            # Determine confidence level
            if gauge.get('qualityVerified', False):
                confidence = 'HIGH (Verified)'
            else:
                confidence = 'LOWER (Unverified)'
            
            writer.writerow({
                'gauge_id': gauge.get('gaugeId', ''),
                'latitude': loc.get('latitude', ''),
                'longitude': loc.get('longitude', ''),
                'river': gauge.get('river', ''),
                'site_name': gauge.get('siteName', ''),
                'quality_verified': gauge.get('qualityVerified', False),
                'has_model': gauge.get('hasModel', False),
                'source': gauge.get('source', ''),
                'confidence_level': confidence
            })
    
    print(f"\n💾 Exported to {csv_filename}")
    
    # Export JSON summary
    summary = {
        "discovery_timestamp": datetime.now().isoformat(),
        "total_gauges": len(gauges),
        "quality_verified": quality_verified,
        "has_model": has_model,
        "gauge_ids": [g.get('gaugeId', '') for g in gauges],
        "discovery_method": "Enhanced search with includeNonQualityVerified"
    }
    
    with open('enhanced_discovery_summary.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"📊 Exported summary to enhanced_discovery_summary.json")

def main():
    """Main execution"""
    print("🚀 ENHANCED PAKISTANI GAUGE DISCOVERY")
    print(f"Started: {datetime.now().isoformat()}")
    print("="*60)
    
    all_discovered = []
    
    # Method 1: Direct gauge queries
    direct_gauges = try_direct_gauge_queries()
    all_discovered.extend(direct_gauges)
    print(f"\n→ Direct queries found: {len(direct_gauges)} gauges")
    
    # Method 2: Batch get
    batch_gauges = try_batch_get()
    all_discovered.extend(batch_gauges)
    print(f"→ Batch get found: {len(batch_gauges)} gauges")
    
    # Method 3: Grid search
    grid_gauges = search_by_grid()
    all_discovered.extend(grid_gauges)
    print(f"→ Grid search found: {len(grid_gauges)} gauges")
    
    # Analyze and export
    analyze_and_export_gauges(all_discovered)
    
    print("\n✅ DISCOVERY COMPLETE")
    print("="*60)
    print("Note: If limited gauges found, consider:")
    print("  1. API may require specific Google Cloud project setup")
    print("  2. Geographic filtering might not be supported")
    print("  3. Try accessing gauge IDs directly if you have a list")

if __name__ == "__main__":
    main()