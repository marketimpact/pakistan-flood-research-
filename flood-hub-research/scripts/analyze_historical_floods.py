#!/usr/bin/env python3
"""
Analyze historical flood data from Google Cloud Storage
Focus on Pakistan region, especially Chitral area
"""

import json
import urllib.request
from datetime import datetime

# Pakistan grid coordinates (5-degree tiles)
PAKISTAN_TILES = [
    # Northern Pakistan (including Chitral, GB, KPK)
    (35.0, 70.0),  # Includes Chitral area
    (35.0, 75.0),  # Eastern KPK, Kashmir
    
    # Central Pakistan
    (30.0, 70.0),  # Western Punjab, Eastern Balochistan
    (30.0, 75.0),  # Eastern Punjab
    
    # Southern Pakistan  
    (25.0, 65.0),  # Western Balochistan
    (25.0, 70.0),  # Eastern Balochistan, Western Sindh
    (25.0, 75.0),  # Eastern Sindh (if exists)
]

BASE_URL = "https://storage.googleapis.com/flood-forecasting/inundation_history/data/"

def download_geojson(lat, lon):
    """Download historical flood data for a specific tile"""
    filename = f"inundation_history_{lat:.3f}_{lon:.3f}.geojson"
    url = BASE_URL + filename
    
    print(f"\n📥 Downloading {filename}...")
    
    try:
        with urllib.request.urlopen(url) as response:
            data = json.loads(response.read().decode())
            print(f"   ✓ Success! Found {len(data.get('features', []))} flood events")
            return data
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"   ✗ No data for this tile")
        else:
            print(f"   ✗ Error: {e}")
        return None
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return None

def analyze_flood_history(geojson_data, lat, lon):
    """Analyze historical flood patterns"""
    if not geojson_data or 'features' not in geojson_data:
        return None
        
    features = geojson_data['features']
    
    analysis = {
        'tile': f"{lat}_{lon}",
        'total_events': len(features),
        'date_range': {'earliest': None, 'latest': None},
        'severity_distribution': {},
        'chitral_events': 0,
        'major_floods': []
    }
    
    for feature in features:
        props = feature.get('properties', {})
        
        # Check if near Chitral (rough check)
        if lat == 35.0 and lon == 70.0:
            geometry = feature.get('geometry', {})
            if geometry.get('type') == 'Polygon':
                # Simple check if coordinates are near Chitral (36.385, 72.206)
                coords = geometry.get('coordinates', [[]])[0]
                for coord in coords:
                    if len(coord) >= 2:
                        if 36.0 < coord[1] < 37.0 and 71.5 < coord[0] < 73.0:
                            analysis['chitral_events'] += 1
                            break
        
        # Extract dates
        date_str = props.get('date') or props.get('timestamp')
        if date_str:
            if not analysis['date_range']['earliest'] or date_str < analysis['date_range']['earliest']:
                analysis['date_range']['earliest'] = date_str
            if not analysis['date_range']['latest'] or date_str > analysis['date_range']['latest']:
                analysis['date_range']['latest'] = date_str
        
        # Severity/magnitude
        severity = props.get('severity') or props.get('magnitude') or 'unknown'
        analysis['severity_distribution'][severity] = analysis['severity_distribution'].get(severity, 0) + 1
        
        # Major floods (if area is large)
        area = props.get('area_km2', 0)
        if area > 100:  # Arbitrary threshold for "major"
            analysis['major_floods'].append({
                'date': date_str,
                'area_km2': area,
                'severity': severity
            })
    
    return analysis

def main():
    print("🌊 PAKISTAN HISTORICAL FLOOD DATA ANALYSIS")
    print("="*60)
    print(f"Source: Google Cloud Storage - flood-forecasting bucket")
    print(f"Analysis Date: {datetime.now().isoformat()}")
    
    all_analyses = []
    chitral_specific = None
    
    for lat, lon in PAKISTAN_TILES:
        data = download_geojson(lat, lon)
        if data:
            analysis = analyze_flood_history(data, lat, lon)
            if analysis:
                all_analyses.append(analysis)
                
                # Special handling for Chitral tile
                if lat == 35.0 and lon == 70.0:
                    chitral_specific = analysis
                    
                    # Save Chitral data specifically
                    with open('chitral_historical_floods.json', 'w') as f:
                        json.dump(data, f, indent=2)
                    print(f"   💾 Saved Chitral area data to chitral_historical_floods.json")
    
    # Summary Report
    print("\n" + "="*60)
    print("📊 SUMMARY ANALYSIS")
    print("="*60)
    
    total_events = sum(a['total_events'] for a in all_analyses)
    print(f"\nTotal Historical Flood Events: {total_events}")
    print(f"Tiles with Data: {len(all_analyses)}/{len(PAKISTAN_TILES)}")
    
    print("\nBy Region:")
    for analysis in all_analyses:
        print(f"\n📍 Tile {analysis['tile']}:")
        print(f"   Events: {analysis['total_events']}")
        print(f"   Date Range: {analysis['date_range']['earliest']} to {analysis['date_range']['latest']}")
        print(f"   Severity Distribution: {analysis['severity_distribution']}")
        if analysis['major_floods']:
            print(f"   Major Floods (>100 km²): {len(analysis['major_floods'])}")
    
    # Chitral Specific
    if chitral_specific:
        print(f"\n🚨 CHITRAL AREA ANALYSIS (Tile 35_70):")
        print(f"   Total Events in Tile: {chitral_specific['total_events']}")
        print(f"   Events Near Chitral: {chitral_specific['chitral_events']}")
        print(f"   Historical Context: {'FREQUENT' if chitral_specific['chitral_events'] > 5 else 'OCCASIONAL' if chitral_specific['chitral_events'] > 0 else 'RARE'} flooding")
    
    # Export comprehensive report
    report = {
        'metadata': {
            'analysis_date': datetime.now().isoformat(),
            'source': 'Google Cloud Storage flood-forecasting bucket',
            'tiles_analyzed': len(PAKISTAN_TILES),
            'tiles_with_data': len(all_analyses)
        },
        'summary': {
            'total_flood_events': total_events,
            'chitral_historical_floods': chitral_specific['chitral_events'] if chitral_specific else 0,
            'coverage_percentage': (len(all_analyses) / len(PAKISTAN_TILES)) * 100
        },
        'regional_analysis': all_analyses
    }
    
    with open('pakistan_flood_history_analysis.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n💾 Comprehensive report saved to pakistan_flood_history_analysis.json")
    
    # Implications for Pak-FEWS
    print("\n" + "="*60)
    print("🎯 IMPLICATIONS FOR PAK-FEWS")
    print("="*60)
    print("1. Historical Validation Available: Can compare predictions to past events")
    print("2. Regional Risk Assessment: Identify historically flood-prone areas")
    print("3. Chitral Context: Assess if current warning aligns with history")
    print("4. System Calibration: Use historical data to validate thresholds")
    
    print("\n✅ ANALYSIS COMPLETE")

if __name__ == "__main__":
    main()