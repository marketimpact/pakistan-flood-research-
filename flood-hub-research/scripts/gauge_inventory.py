#!/usr/bin/env python3
"""
Query and analyze all Pakistani gauges from Google Flood Hub API
Creates comprehensive inventory of flood monitoring coverage
"""

import json
import urllib.request
import urllib.parse
from datetime import datetime
import csv


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

def make_api_request(endpoint, params=None):
    """Make API request using urllib"""
    url = f"{BASE_URL}/{endpoint}"
    
    if params is None:
        params = {}
    params['key'] = API_KEY
    
    # Add API key header as well
    headers = {
        'X-goog-api-key': API_KEY
    }
    
    query_string = urllib.parse.urlencode(params)
    full_url = f"{url}?{query_string}"
    
    request = urllib.request.Request(full_url, headers=headers)
    
    try:
        with urllib.request.urlopen(request) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        print(f"Error making request to {endpoint}: {e}")
        return None

def query_pakistan_gauges():
    """Query all gauges within Pakistan boundaries"""
    print("🔍 QUERYING PAKISTAN GAUGES")
    print(f"Bounds: {PAKISTAN_BOUNDS['min_lat']}°N to {PAKISTAN_BOUNDS['max_lat']}°N, "
          f"{PAKISTAN_BOUNDS['min_lon']}°E to {PAKISTAN_BOUNDS['max_lon']}°E")
    print("="*60)
    
    # Try different endpoint formats
    endpoints_to_try = [
        ('gauges', {}),
        ('gauges:searchByArea', {
            'minLatitude': PAKISTAN_BOUNDS['min_lat'],
            'maxLatitude': PAKISTAN_BOUNDS['max_lat'],
            'minLongitude': PAKISTAN_BOUNDS['min_lon'],
            'maxLongitude': PAKISTAN_BOUNDS['max_lon']
        }),
        ('gauges', {
            'bounds': f"{PAKISTAN_BOUNDS['min_lat']},{PAKISTAN_BOUNDS['min_lon']},"
                     f"{PAKISTAN_BOUNDS['max_lat']},{PAKISTAN_BOUNDS['max_lon']}"
        })
    ]
    
    all_gauges = []
    
    for endpoint, params in endpoints_to_try:
        print(f"\nTrying endpoint: {endpoint}")
        response = make_api_request(endpoint, params)
        
        if response:
            # Handle different response formats
            if isinstance(response, dict) and 'gauges' in response:
                gauges = response['gauges']
            elif isinstance(response, list):
                gauges = response
            else:
                print(f"Unexpected response format: {type(response)}")
                continue
                
            print(f"✓ Found {len(gauges)} gauges")
            
            # Filter for Pakistan bounds
            pakistan_gauges = []
            for gauge in gauges:
                loc = gauge.get('location', {})
                lat = loc.get('latitude', 0)
                lon = loc.get('longitude', 0)
                
                if (PAKISTAN_BOUNDS['min_lat'] <= lat <= PAKISTAN_BOUNDS['max_lat'] and
                    PAKISTAN_BOUNDS['min_lon'] <= lon <= PAKISTAN_BOUNDS['max_lon']):
                    pakistan_gauges.append(gauge)
            
            print(f"  → {len(pakistan_gauges)} within Pakistan bounds")
            
            if pakistan_gauges:
                all_gauges = pakistan_gauges
                break
    
    return all_gauges

def analyze_gauges(gauges):
    """Analyze gauge characteristics"""
    print(f"\n📊 ANALYZING {len(gauges)} PAKISTANI GAUGES")
    print("="*60)
    
    # Statistics
    quality_verified = sum(1 for g in gauges if g.get('qualityVerified', False))
    has_model = sum(1 for g in gauges if g.get('hasModel', False))
    
    # Group by source
    sources = {}
    for gauge in gauges:
        source = gauge.get('source', 'Unknown')
        sources[source] = sources.get(source, 0) + 1
    
    # Group by river
    rivers = {}
    for gauge in gauges:
        river = gauge.get('river', '') or 'Unnamed'
        if river:
            rivers[river] = rivers.get(river, 0) + 1
    
    print(f"\n✅ Quality Verified: {quality_verified}/{len(gauges)} ({quality_verified/len(gauges)*100:.1f}%)")
    print(f"📈 Has Model: {has_model}/{len(gauges)} ({has_model/len(gauges)*100:.1f}%)")
    
    print("\n📍 Sources:")
    for source, count in sorted(sources.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {source}: {count} gauges")
    
    print("\n🌊 Major Rivers (with named gauges):")
    for river, count in sorted(rivers.items(), key=lambda x: x[1], reverse=True)[:10]:
        if river != 'Unnamed':
            print(f"  - {river}: {count} gauges")
    
    # Find major city gauges
    print("\n🏙️ Gauges Near Major Cities:")
    major_cities = {
        'Islamabad': (33.6844, 73.0479),
        'Karachi': (24.8607, 67.0011),
        'Lahore': (31.5497, 74.3436),
        'Peshawar': (34.0151, 71.5249),
        'Quetta': (30.1798, 66.9750),
        'Chitral': (35.8462, 71.7868)
    }
    
    for city, (city_lat, city_lon) in major_cities.items():
        nearby_gauges = []
        for gauge in gauges:
            loc = gauge.get('location', {})
            lat = loc.get('latitude', 0)
            lon = loc.get('longitude', 0)
            
            # Simple distance check (within ~50km)
            if abs(lat - city_lat) < 0.5 and abs(lon - city_lon) < 0.5:
                nearby_gauges.append(gauge)
        
        if nearby_gauges:
            verified = sum(1 for g in nearby_gauges if g.get('qualityVerified', False))
            print(f"  - {city}: {len(nearby_gauges)} gauges ({verified} verified)")

def export_gauge_inventory(gauges):
    """Export gauge inventory to CSV"""
    filename = f"gauge_inventory_pakistan_{datetime.now().strftime('%Y%m%d')}.csv"
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['gauge_id', 'latitude', 'longitude', 'river', 'site_name', 
                     'quality_verified', 'has_model', 'source', 'province_estimate']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for gauge in gauges:
            loc = gauge.get('location', {})
            lat = loc.get('latitude', 0)
            lon = loc.get('longitude', 0)
            
            # Estimate province based on coordinates
            province = estimate_province(lat, lon)
            
            writer.writerow({
                'gauge_id': gauge.get('gaugeId', ''),
                'latitude': lat,
                'longitude': lon,
                'river': gauge.get('river', ''),
                'site_name': gauge.get('siteName', ''),
                'quality_verified': gauge.get('qualityVerified', False),
                'has_model': gauge.get('hasModel', False),
                'source': gauge.get('source', ''),
                'province_estimate': province
            })
    
    print(f"\n💾 Exported to {filename}")
    return filename

def estimate_province(lat, lon):
    """Rough estimate of province based on coordinates"""
    if lat > 35 and lon < 75:
        return "KPK/GB"
    elif lat > 30 and lon > 73:
        return "Punjab"
    elif lat < 28:
        return "Sindh"
    elif lon < 67:
        return "Balochistan"
    else:
        return "Unknown"

def create_coverage_summary(gauges):
    """Create coverage analysis JSON"""
    summary = {
        "metadata": {
            "generated": datetime.now().isoformat(),
            "total_gauges": len(gauges),
            "bounds": PAKISTAN_BOUNDS
        },
        "quality_metrics": {
            "quality_verified": sum(1 for g in gauges if g.get('qualityVerified', False)),
            "has_model": sum(1 for g in gauges if g.get('hasModel', False)),
            "both_verified_and_model": sum(1 for g in gauges if g.get('qualityVerified', False) and g.get('hasModel', False))
        },
        "sources": {},
        "major_rivers": [],
        "coverage_gaps": []
    }
    
    # Count sources
    for gauge in gauges:
        source = gauge.get('source', 'Unknown')
        summary['sources'][source] = summary['sources'].get(source, 0) + 1
    
    # Identify major rivers
    river_counts = {}
    for gauge in gauges:
        river = gauge.get('river', '')
        if river:
            river_counts[river] = river_counts.get(river, 0) + 1
    
    summary['major_rivers'] = [
        {"river": river, "gauge_count": count}
        for river, count in sorted(river_counts.items(), key=lambda x: x[1], reverse=True)
        if count >= 3  # Rivers with 3+ gauges
    ]
    
    # Export summary
    with open('coverage_analysis.json', 'w') as f:
        json.dump(summary, f, indent=2)
    
    print("📊 Exported coverage analysis to coverage_analysis.json")

def main():
    """Main execution"""
    print("🚀 GOOGLE FLOOD HUB PAKISTAN GAUGE INVENTORY")
    print(f"Started: {datetime.now().isoformat()}")
    print("="*60)
    
    # Query gauges
    gauges = query_pakistan_gauges()
    
    if not gauges:
        print("\n❌ No gauges found. Check API connection.")
        return
    
    # Analyze
    analyze_gauges(gauges)
    
    # Export
    csv_file = export_gauge_inventory(gauges)
    create_coverage_summary(gauges)
    
    # Special focus on quality verified gauges
    quality_gauges = [g for g in gauges if g.get('qualityVerified', False)]
    print(f"\n🏆 QUALITY VERIFIED GAUGES ({len(quality_gauges)}):")
    for gauge in quality_gauges[:10]:  # Show first 10
        print(f"  - {gauge.get('gaugeId')}: {gauge.get('river', 'Unknown river')} "
              f"@ {gauge.get('location', {}).get('latitude'):.3f}, "
              f"{gauge.get('location', {}).get('longitude'):.3f}")
    
    if len(quality_gauges) > 10:
        print(f"  ... and {len(quality_gauges) - 10} more")
    
    print("\n✅ INVENTORY COMPLETE")
    print(f"Files created: {csv_file}, coverage_analysis.json")

if __name__ == "__main__":
    main()