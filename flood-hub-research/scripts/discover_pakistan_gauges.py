#!/usr/bin/env python3
"""
Discover Pakistani Gauges
Since area search isn't available, we'll try different approaches to find Pakistani gauges
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import json
import time
import pandas as pd
from datetime import datetime
from typing import List, Dict, Optional

from scripts.flood_hub_api import FloodHubAPI


class PakistanGaugeDiscovery:
    """Discover Pakistani gauges through various methods"""
    
    def __init__(self, api_key: str):
        self.api = FloodHubAPI(api_key=api_key)
        self.discovered_gauges = []
        
    def test_known_gauge_ids(self) -> List[Dict]:
        """Test known gauge IDs from documentation"""
        
        # Known gauge IDs from CLAUDE.md and documentation
        known_ids = [
            "hybas_4121489010",
            "hybas_6120111530",
            # Generate some possible Pakistani gauge IDs based on patterns
            "hybas_4121489020",
            "hybas_4121489030", 
            "hybas_4121489040",
            "hybas_6120111540",
            "hybas_6120111550",
            # Try PMD (Pakistan Meteorological Department) patterns
            "pmd_pk_001", "pmd_pk_002", "pmd_pk_003",
            # Try WAPDA (Water and Power Development Authority) patterns  
            "wapda_pk_001", "wapda_pk_002", "wapda_pk_003",
            # Try HYBAS patterns for South Asia region
            "hybas_412148901", "hybas_412148902", "hybas_412148903",
            "hybas_612011153", "hybas_612011154", "hybas_612011155"
        ]
        
        print(f"Testing {len(known_ids)} known/potential gauge IDs...")
        working_gauges = []
        
        for gauge_id in known_ids:
            try:
                print(f"  Testing: {gauge_id}")
                gauge_data = self.api.get_gauge_details(gauge_id)
                
                # Check if this is in Pakistan region
                location = gauge_data.get('location', {})
                lat = location.get('latitude', 0)
                lon = location.get('longitude', 0)
                
                # Pakistan bounds: 23-37°N, 60-77°E
                if 23 <= lat <= 37 and 60 <= lon <= 77:
                    print(f"    ✓ Found Pakistani gauge: {gauge_id}")
                    working_gauges.append(gauge_data)
                else:
                    print(f"    - Outside Pakistan: {lat:.2f}, {lon:.2f}")
                    
                time.sleep(0.1)  # Rate limiting
                
            except Exception as e:
                print(f"    ✗ Failed: {str(e)[:50]}...")
                continue
                
        return working_gauges
    
    def scan_hybas_range(self, base_id: str, start: int, end: int) -> List[Dict]:
        """Scan a range of HYBAS IDs systematically"""
        
        print(f"Scanning HYBAS range {base_id}{start:03d} to {base_id}{end:03d}...")
        found_gauges = []
        
        for i in range(start, end + 1):
            gauge_id = f"{base_id}{i:03d}"
            
            try:
                gauge_data = self.api.get_gauge_details(gauge_id)
                location = gauge_data.get('location', {})
                lat = location.get('latitude', 0)
                lon = location.get('longitude', 0)
                
                # Check if in Pakistan
                if 23 <= lat <= 37 and 60 <= lon <= 77:
                    print(f"  ✓ Found: {gauge_id} at {lat:.3f}, {lon:.3f}")
                    found_gauges.append(gauge_data)
                    
                time.sleep(0.1)  # Rate limiting
                
            except Exception:
                continue  # Expected for non-existent gauges
                
        return found_gauges
    
    def discover_via_flood_status(self) -> List[Dict]:
        """Try to discover gauges through flood status endpoint"""
        
        print("Attempting to discover gauges via flood status...")
        
        try:
            # Try different flood status endpoints
            endpoints = ['floodStatus', 'floodStatus:list', 'floodStatus:search']
            
            for endpoint in endpoints:
                try:
                    print(f"  Trying: {endpoint}")
                    response = self.api._make_request(endpoint)
                    
                    # If successful, extract gauge IDs
                    if isinstance(response, dict):
                        print(f"    Got response type: {type(response)}")
                        print(f"    Keys: {list(response.keys()) if response else 'None'}")
                        
                        # Look for gauge references
                        gauges_found = self.extract_gauge_ids_from_response(response)
                        if gauges_found:
                            return gauges_found
                            
                except Exception as e:
                    print(f"    Failed: {str(e)[:50]}...")
                    continue
                    
        except Exception as e:
            print(f"Flood status discovery failed: {e}")
            
        return []
    
    def extract_gauge_ids_from_response(self, response: Dict) -> List[str]:
        """Extract gauge IDs from API response"""
        gauge_ids = []
        
        def recursive_search(obj, path=""):
            if isinstance(obj, dict):
                for key, value in obj.items():
                    if 'gauge' in key.lower() and 'id' in key.lower():
                        if isinstance(value, str):
                            gauge_ids.append(value)
                    recursive_search(value, f"{path}.{key}")
            elif isinstance(obj, list):
                for i, item in enumerate(obj):
                    recursive_search(item, f"{path}[{i}]")
        
        recursive_search(response)
        return gauge_ids
    
    def comprehensive_discovery(self) -> List[Dict]:
        """Run comprehensive gauge discovery"""
        
        print("Starting Comprehensive Pakistani Gauge Discovery")
        print("=" * 55)
        
        all_gauges = []
        
        # Method 1: Test known IDs
        print("\n1. Testing known gauge IDs...")
        known_gauges = self.test_known_gauge_ids()
        all_gauges.extend(known_gauges)
        print(f"   Found {len(known_gauges)} gauges from known IDs")
        
        # Method 2: Scan HYBAS ranges (based on successful IDs)
        if known_gauges:
            print("\n2. Scanning nearby HYBAS ranges...")
            
            # Extract base patterns from successful gauges
            hybas_bases = set()
            for gauge in known_gauges:
                gauge_id = gauge.get('gaugeId', '')
                if gauge_id.startswith('hybas_'):
                    # Extract base pattern (e.g., "hybas_41214890" from "hybas_4121489010")
                    base = gauge_id[:12]  # First 12 characters
                    hybas_bases.add(base)
            
            for base in hybas_bases:
                range_gauges = self.scan_hybas_range(base, 0, 50)
                all_gauges.extend(range_gauges)
                print(f"   Found {len(range_gauges)} gauges in range {base}...")
        
        # Method 3: Try flood status discovery
        print("\n3. Attempting flood status discovery...")
        status_gauges = self.discover_via_flood_status()
        print(f"   Found {len(status_gauges)} gauges from flood status")
        
        # Remove duplicates
        unique_gauges = []
        seen_ids = set()
        
        for gauge in all_gauges:
            gauge_id = gauge.get('gaugeId')
            if gauge_id and gauge_id not in seen_ids:
                unique_gauges.append(gauge)
                seen_ids.add(gauge_id)
        
        print(f"\n✓ Discovery complete: {len(unique_gauges)} unique Pakistani gauges found")
        return unique_gauges


def analyze_discovered_gauges(gauges: List[Dict]) -> Dict:
    """Analyze the discovered gauges"""
    
    if not gauges:
        return {"error": "No gauges found"}
    
    # Create DataFrame for analysis
    df_data = []
    for gauge in gauges:
        location = gauge.get('location', {})
        row = {
            'gaugeId': gauge.get('gaugeId', ''),
            'latitude': location.get('latitude'),
            'longitude': location.get('longitude'),
            'river': gauge.get('river', ''),
            'siteName': gauge.get('siteName', ''),
            'qualityVerified': gauge.get('qualityVerified', False),
            'hasModel': gauge.get('hasModel', False),
            'source': gauge.get('source', ''),
            'countryCode': gauge.get('countryCode', '')
        }
        df_data.append(row)
    
    df = pd.DataFrame(df_data)
    
    # Analysis
    analysis = {
        'total_gauges': len(df),
        'quality_verified': len(df[df['qualityVerified'] == True]),
        'has_model': len(df[df['hasModel'] == True]),
        'both_quality_and_model': len(df[(df['qualityVerified'] == True) & (df['hasModel'] == True)]),
        'sources': df['source'].value_counts().to_dict(),
        'rivers_named': len(df[df['river'] != '']),
        'unique_rivers': df[df['river'] != '']['river'].nunique() if len(df[df['river'] != '']) > 0 else 0,
        'coordinate_range': {
            'lat_min': float(df['latitude'].min()) if df['latitude'].notna().any() else None,
            'lat_max': float(df['latitude'].max()) if df['latitude'].notna().any() else None,
            'lon_min': float(df['longitude'].min()) if df['longitude'].notna().any() else None,
            'lon_max': float(df['longitude'].max()) if df['longitude'].notna().any() else None,
        }
    }
    
    return analysis


def main():
    """Main execution"""
    
    api_key = "AIzaSyB0d7jLuqXjDJW_BQxOyCrBVt97zse7S-M"
    discovery = PakistanGaugeDiscovery(api_key)
    
    # Run comprehensive discovery
    gauges = discovery.comprehensive_discovery()
    
    if gauges:
        # Save raw data
        os.makedirs('data', exist_ok=True)
        
        with open('data/discovered_pakistan_gauges.json', 'w') as f:
            json.dump(gauges, f, indent=2)
        
        # Create DataFrame and save CSV
        df_data = []
        for gauge in gauges:
            location = gauge.get('location', {})
            row = {
                'gaugeId': gauge.get('gaugeId', ''),
                'latitude': location.get('latitude'),
                'longitude': location.get('longitude'),
                'river': gauge.get('river', ''),
                'siteName': gauge.get('siteName', ''),
                'qualityVerified': gauge.get('qualityVerified', False),
                'hasModel': gauge.get('hasModel', False),
                'source': gauge.get('source', ''),
                'countryCode': gauge.get('countryCode', ''),
                'discovery_timestamp': datetime.now().isoformat()
            }
            df_data.append(row)
        
        df = pd.DataFrame(df_data)
        df.to_csv('data/real_pakistan_gauges.csv', index=False)
        
        # Analyze
        analysis = analyze_discovered_gauges(gauges)
        
        with open('data/real_gauge_analysis.json', 'w') as f:
            json.dump(analysis, f, indent=2)
        
        # Print results
        print("\n" + "=" * 55)
        print("REAL PAKISTANI GAUGE ANALYSIS")
        print("=" * 55)
        print(f"Total gauges discovered: {analysis['total_gauges']}")
        print(f"Quality verified: {analysis['quality_verified']}")
        print(f"Has model: {analysis['has_model']}")
        print(f"Both quality + model: {analysis['both_quality_and_model']}")
        print(f"Rivers with names: {analysis['rivers_named']}")
        print(f"Unique rivers: {analysis['unique_rivers']}")
        
        print(f"\nCoordinate coverage:")
        coord_range = analysis['coordinate_range']
        if coord_range['lat_min']:
            print(f"  Latitude: {coord_range['lat_min']:.3f} to {coord_range['lat_max']:.3f}")
            print(f"  Longitude: {coord_range['lon_min']:.3f} to {coord_range['lon_max']:.3f}")
        
        print(f"\nData sources:")
        for source, count in analysis['sources'].items():
            print(f"  {source}: {count}")
        
        print(f"\nFiles saved:")
        print(f"  • data/discovered_pakistan_gauges.json")
        print(f"  • data/real_pakistan_gauges.csv")
        print(f"  • data/real_gauge_analysis.json")
        
    else:
        print("\n✗ No Pakistani gauges could be discovered")
        print("Recommendations:")
        print("• Verify API key has Flood Hub access")
        print("• Try applying for enhanced API access")
        print("• Use mock data for development")


if __name__ == "__main__":
    main()