#!/usr/bin/env python3
"""
Mock Data Generator for Google Flood Hub API
Creates realistic sample data based on API documentation for testing purposes
"""

import json
import random
from typing import List, Dict
from datetime import datetime, timedelta


class MockFloodHubData:
    """Generate mock data that matches Google Flood Hub API structure"""
    
    # Sample gauge IDs from documentation and typical formats
    SAMPLE_GAUGE_IDS = [
        "hybas_4121489010",
        "hybas_6120111530", 
        "hybas_4121489020",
        "hybas_4121489030",
        "pk_pmd_001",
        "pk_pmd_002",
        "pk_wapda_001",
        "pk_wapda_002"
    ]
    
    # Pakistani rivers
    PAKISTANI_RIVERS = [
        "Indus", "Jhelum", "Chenab", "Ravi", "Sutlej",
        "Kabul", "Kurram", "Chitral", "Shyok", "Hunza",
        "Gilgit", "Swat", "Shah Alam", "Kuram"
    ]
    
    # Pakistani cities/locations
    PAKISTANI_LOCATIONS = [
        "Tarbela", "Mangla", "Sukkur", "Kotri", "Chashma",
        "Kalabagh", "Nowshera", "Mardan", "Chitral", "Gilgit",
        "Skardu", "Attock", "Sialkot", "Gujranwala", "Multan",
        "Bahawalpur", "Hyderabad", "Jacobabad", "Larkana"
    ]
    
    # Province coordinates (center points)
    PROVINCE_COORDS = {
        'Punjab': [(31.1704, 72.7097), (30.3753, 69.3451), (29.3956, 71.6836)],
        'Sindh': [(25.8943, 68.5247), (26.2442, 67.8307), (27.0238, 67.0822)],
        'Khyber Pakhtunkhwa': [(34.0151, 71.5249), (33.9969, 72.8397), (35.2226, 72.4258)],
        'Balochistan': [(30.1798, 66.9750), (28.3588, 65.0377), (29.8406, 67.0011)],
        'Gilgit-Baltistan': [(35.9042, 74.3086), (36.0761, 76.0958), (35.1654, 75.3301)]
    }
    
    def generate_mock_gauges(self, count: int = 50) -> List[Dict]:
        """Generate mock gauge data for Pakistan"""
        gauges = []
        
        for i in range(count):
            # Pick random province and coordinates
            province = random.choice(list(self.PROVINCE_COORDS.keys()))
            base_coords = random.choice(self.PROVINCE_COORDS[province])
            
            # Add some variation to coordinates
            lat = base_coords[0] + random.uniform(-0.5, 0.5)
            lon = base_coords[1] + random.uniform(-0.5, 0.5)
            
            # Ensure coordinates are within Pakistan bounds
            lat = max(23.0, min(37.0, lat))
            lon = max(60.0, min(77.0, lon))
            
            gauge = {
                "gaugeId": f"pk_{province.lower().replace(' ', '_')}_{i:03d}",
                "location": {
                    "latitude": round(lat, 6),
                    "longitude": round(lon, 6)
                },
                "siteName": random.choice(self.PAKISTANI_LOCATIONS),
                "river": random.choice(self.PAKISTANI_RIVERS) if random.random() > 0.2 else "",
                "source": random.choice(["HYBAS", "PMD", "WAPDA", "SUPARCO"]),
                "qualityVerified": random.random() > 0.4,  # ~60% quality verified
                "hasModel": random.random() > 0.3,  # ~70% have models
                "countryCode": "PK"
            }
            
            gauges.append(gauge)
            
        return gauges
    
    def generate_mock_flood_status(self, gauge_id: str) -> Dict:
        """Generate mock flood status for a gauge"""
        severities = ["NONE", "MINOR", "MODERATE", "SEVERE", "EXTREME"]
        trends = ["STABLE", "RISING", "FALLING"]
        
        status = {
            "gaugeId": gauge_id,
            "severity": random.choice(severities),
            "forecastTrend": random.choice(trends),
            "thresholds": {
                "warningLevel": round(random.uniform(1000, 3000), 2),
                "dangerLevel": round(random.uniform(3000, 6000), 2), 
                "extremeDangerLevel": round(random.uniform(6000, 10000), 2)
            },
            "gaugeValueUnit": random.choice(["CUBIC_METERS_PER_SECOND", "METERS"]),
            "currentLevel": round(random.uniform(500, 8000), 2),
            "forecastTimestamp": (datetime.now() + timedelta(hours=24)).isoformat(),
            "hasInundationMap": random.random() > 0.5
        }
        
        return status
    
    def generate_mock_gauge_model(self, gauge_id: str) -> Dict:
        """Generate mock gauge model/threshold data"""
        return {
            "gaugeId": gauge_id,
            "thresholds": {
                "warningLevel": round(random.uniform(1000, 3000), 2),
                "dangerLevel": round(random.uniform(3000, 6000), 2),
                "extremeDangerLevel": round(random.uniform(6000, 10000), 2)
            },
            "units": random.choice(["CUBIC_METERS_PER_SECOND", "METERS"]),
            "returnPeriods": {
                "twoYear": round(random.uniform(800, 2000), 2),
                "fiveYear": round(random.uniform(2000, 4000), 2),
                "twentyYear": round(random.uniform(4000, 8000), 2)
            },
            "modelType": random.choice(["HYDRAULIC", "HYDROLOGICAL", "STATISTICAL"]),
            "lastUpdated": datetime.now().isoformat()
        }


def create_sample_datasets():
    """Create sample datasets for testing the research approach"""
    mock_data = MockFloodHubData()
    
    # Generate gauge inventory
    print("Generating mock Pakistani gauge inventory...")
    gauges = mock_data.generate_mock_gauges(75)  # Realistic number for Pakistan
    
    # Save gauge inventory
    with open('data/sample_gauge_inventory.json', 'w') as f:
        json.dump(gauges, f, indent=2)
    print(f"Created sample_gauge_inventory.json with {len(gauges)} gauges")
    
    # Generate flood status for quality verified gauges
    quality_gauges = [g for g in gauges if g['qualityVerified']]
    print(f"Generating flood status for {len(quality_gauges)} quality verified gauges...")
    
    flood_statuses = []
    for gauge in quality_gauges[:20]:  # Sample subset
        status = mock_data.generate_mock_flood_status(gauge['gaugeId'])
        flood_statuses.append(status)
    
    with open('data/sample_flood_status.json', 'w') as f:
        json.dump(flood_statuses, f, indent=2)
    print(f"Created sample_flood_status.json with {len(flood_statuses)} status records")
    
    # Generate gauge models
    model_gauges = [g for g in gauges if g['hasModel']]
    print(f"Generating models for {len(model_gauges)} gauges with models...")
    
    gauge_models = []
    for gauge in model_gauges[:15]:  # Sample subset
        model = mock_data.generate_mock_gauge_model(gauge['gaugeId'])
        gauge_models.append(model)
    
    with open('data/sample_gauge_models.json', 'w') as f:
        json.dump(gauge_models, f, indent=2)
    print(f"Created sample_gauge_models.json with {len(gauge_models)} model records")
    
    # Print summary
    print("\n" + "="*50)
    print("MOCK DATA SUMMARY")  
    print("="*50)
    print(f"Total gauges: {len(gauges)}")
    print(f"Quality verified: {len(quality_gauges)}")
    print(f"Have models: {len(model_gauges)}")
    print(f"Both quality verified AND have models: {len([g for g in gauges if g['qualityVerified'] and g['hasModel']])}")
    
    # Show by province distribution
    print("\nDistribution by Province:")
    for province in MockFloodHubData.PROVINCE_COORDS.keys():
        count = len([g for g in gauges if province.lower().replace(' ', '_') in g['gaugeId']])
        print(f"  {province}: {count}")
    
    print(f"\nFiles created in data/ directory:")
    print("- sample_gauge_inventory.json")
    print("- sample_flood_status.json") 
    print("- sample_gauge_models.json")


if __name__ == "__main__":
    import os
    os.makedirs('data', exist_ok=True)
    create_sample_datasets()