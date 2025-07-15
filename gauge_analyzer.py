#!/usr/bin/env python3
"""
Pakistan Flood Hub Gauge Analyzer
Identifies and classifies physical vs virtual river gauges for Pakistan
"""

import requests
import json
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import logging
from dataclasses import dataclass
from geopy.distance import geodesic

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class GaugeInfo:
    """Data structure for gauge information"""
    gauge_id: str
    location: Dict[str, float]
    source: str
    site_name: str
    river: str
    quality_verified: bool
    has_model: bool
    confidence_score: int = 0
    evidence: List[str] = None
    classification: str = ""
    
    def __post_init__(self):
        if self.evidence is None:
            self.evidence = []

class GaugeClassification:
    """Classification system for gauge types"""
    VERIFIED_PHYSICAL = "verified_physical"      # 100% certain
    LIKELY_PHYSICAL = "likely_physical"          # 70%+ confidence
    UNCERTAIN = "uncertain"                      # 30-70% confidence  
    LIKELY_VIRTUAL = "likely_virtual"            # <30% confidence

class PakistanGaugeAnalyzer:
    """Main analyzer class for Pakistani river gauges"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://floodhub.googleapis.com"
        
        # Pakistan bounding box
        self.pakistan_bounds = {
            "min_lat": 23.5,
            "max_lat": 37.5,
            "min_lon": 60.5,
            "max_lon": 77.5
        }
        
        # Known physical stations in Pakistan
        self.known_stations = {
            # Indus River
            "Tarbela": (33.9, 72.7),
            "Kalabagh": (32.96, 71.55),
            "Chashma": (32.45, 71.35),
            "Sukkur": (27.7, 68.85),
            "Kotri": (25.37, 68.31),
            
            # Chenab River  
            "Marala": (32.67, 74.46),
            "Khanki": (31.30, 73.58),
            "Qadirabad": (31.40, 73.52),
            
            # Jhelum River
            "Mangla": (33.13, 73.64),
            "Rasul": (31.36, 73.52),
            
            # Kabul River
            "Nowshera": (34.02, 71.98),
            
            # Sutlej River
            "Sulemanki": (30.07, 73.07)
        }
        
        self.gauges_data = []
        
    def fetch_pakistan_gauges(self) -> List[Dict]:
        """Fetch all gauges within Pakistan boundaries"""
        try:
            # Note: This is a placeholder URL structure
            # The actual API endpoint structure needs to be confirmed
            url = f"{self.base_url}/v1/gauges"
            
            params = {
                "bounds": f"{self.pakistan_bounds['min_lat']},{self.pakistan_bounds['min_lon']},{self.pakistan_bounds['max_lat']},{self.pakistan_bounds['max_lon']}"
            }
            
            if self.api_key:
                params["key"] = self.api_key
                
            logger.info(f"Fetching gauges from: {url}")
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            gauges = data.get('gauges', [])
            
            logger.info(f"Found {len(gauges)} gauges in Pakistan region")
            return gauges
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return []
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return []
    
    def analyze_gauge_physicality(self, gauge: Dict) -> GaugeInfo:
        """Analyze a single gauge to determine if it's physical or virtual"""
        gauge_info = GaugeInfo(
            gauge_id=gauge.get('gaugeId', ''),
            location=gauge.get('location', {}),
            source=gauge.get('source', ''),
            site_name=gauge.get('siteName', ''),
            river=gauge.get('river', ''),
            quality_verified=gauge.get('qualityVerified', False),
            has_model=gauge.get('hasModel', False)
        )
        
        confidence_score = 0
        evidence = []
        
        # Check 1: Named site or river (strong indicator of physical gauge)
        if gauge_info.site_name.strip():
            confidence_score += 30
            evidence.append(f"Named site: {gauge_info.site_name}")
        
        if gauge_info.river.strip():
            confidence_score += 20
            evidence.append(f"Named river: {gauge_info.river}")
        
        # Check 2: Source type (most important indicator)
        if gauge_info.source in ['GRDC', 'WAPDA', 'PMD']:
            confidence_score += 40
            evidence.append(f"Physical network: {gauge_info.source}")
        elif gauge_info.source == 'HYBAS':
            # HYBAS could be physical or virtual - needs additional verification
            confidence_score += 10
            evidence.append("HYBAS - needs verification")
        else:
            evidence.append(f"Unknown source: {gauge_info.source}")
        
        # Check 3: Quality verified (indicates real data validation)
        if gauge_info.quality_verified:
            confidence_score += 10
            evidence.append("Quality verified")
        
        # Check 4: Gauge ID pattern analysis
        if not gauge_info.gauge_id.startswith('hybas_'):
            confidence_score += 20
            evidence.append("Non-HYBAS ID format")
        
        # Check 5: Match with known physical stations
        match_distance = self._find_closest_known_station(gauge_info.location)
        if match_distance is not None and match_distance < 1.0:  # Within 1km
            confidence_score += 30
            evidence.append(f"Matches known station (within {match_distance:.2f}km)")
        
        # Determine classification
        if confidence_score >= 70:
            classification = GaugeClassification.LIKELY_PHYSICAL
        elif confidence_score >= 50:
            classification = GaugeClassification.UNCERTAIN
        elif confidence_score >= 30:
            classification = GaugeClassification.UNCERTAIN
        else:
            classification = GaugeClassification.LIKELY_VIRTUAL
        
        gauge_info.confidence_score = confidence_score
        gauge_info.evidence = evidence
        gauge_info.classification = classification
        
        return gauge_info
    
    def _find_closest_known_station(self, location: Dict) -> Optional[float]:
        """Find distance to closest known physical station"""
        if not location or 'latitude' not in location or 'longitude' not in location:
            return None
        
        gauge_coords = (location['latitude'], location['longitude'])
        min_distance = float('inf')
        
        for station_name, station_coords in self.known_stations.items():
            try:
                distance = geodesic(gauge_coords, station_coords).kilometers
                min_distance = min(min_distance, distance)
            except Exception:
                continue
        
        return min_distance if min_distance != float('inf') else None
    
    def analyze_all_gauges(self) -> pd.DataFrame:
        """Analyze all Pakistani gauges and return classification results"""
        logger.info("Starting gauge analysis...")
        
        # Fetch gauges from API
        raw_gauges = self.fetch_pakistan_gauges()
        
        if not raw_gauges:
            logger.warning("No gauges fetched - using sample data for testing")
            raw_gauges = self._get_sample_data()
        
        # Analyze each gauge
        analyzed_gauges = []
        for gauge in raw_gauges:
            gauge_info = self.analyze_gauge_physicality(gauge)
            analyzed_gauges.append(gauge_info)
        
        # Convert to DataFrame
        df_data = []
        for gauge in analyzed_gauges:
            df_data.append({
                'gaugeId': gauge.gauge_id,
                'latitude': gauge.location.get('latitude', 0),
                'longitude': gauge.location.get('longitude', 0),
                'source': gauge.source,
                'siteName': gauge.site_name,
                'river': gauge.river,
                'qualityVerified': gauge.quality_verified,
                'hasModel': gauge.has_model,
                'confidenceScore': gauge.confidence_score,
                'classification': gauge.classification,
                'evidence': '; '.join(gauge.evidence),
                'lastVerified': datetime.now().strftime('%Y-%m-%d')
            })
        
        df = pd.DataFrame(df_data)
        logger.info(f"Analyzed {len(df)} gauges")
        
        return df
    
    def _get_sample_data(self) -> List[Dict]:
        """Sample data for testing when API is not available"""
        return [
            {
                "gaugeId": "PKGR0001",
                "location": {"latitude": 33.9, "longitude": 72.7},
                "source": "GRDC",
                "siteName": "Tarbela Dam",
                "river": "Indus River",
                "qualityVerified": True,
                "hasModel": True
            },
            {
                "gaugeId": "hybas_4121489010",
                "location": {"latitude": 26.060416666665333, "longitude": 68.931249999995941},
                "source": "HYBAS",
                "siteName": "",
                "river": "",
                "qualityVerified": True,
                "hasModel": True
            },
            {
                "gaugeId": "WAPDA_001",
                "location": {"latitude": 32.96, "longitude": 71.55},
                "source": "WAPDA",
                "siteName": "Kalabagh Barrage",
                "river": "Indus River",
                "qualityVerified": True,
                "hasModel": True
            }
        ]
    
    def generate_reports(self, df: pd.DataFrame) -> Dict:
        """Generate summary reports and statistics"""
        reports = {}
        
        # Classification summary
        classification_counts = df['classification'].value_counts()
        reports['classification_summary'] = classification_counts.to_dict()
        
        # Source analysis
        source_counts = df['source'].value_counts()
        reports['source_summary'] = source_counts.to_dict()
        
        # Quality verification stats
        quality_stats = df['qualityVerified'].value_counts()
        reports['quality_summary'] = quality_stats.to_dict()
        
        # High confidence physical gauges
        physical_gauges = df[df['classification'] == GaugeClassification.LIKELY_PHYSICAL]
        reports['physical_gauge_count'] = len(physical_gauges)
        
        # Geographic distribution
        reports['geographic_stats'] = {
            'latitude_range': [df['latitude'].min(), df['latitude'].max()],
            'longitude_range': [df['longitude'].min(), df['longitude'].max()],
            'total_gauges': len(df)
        }
        
        return reports
    
    def save_results(self, df: pd.DataFrame, reports: Dict):
        """Save analysis results to files"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save gauge inventory CSV
        csv_filename = f'gauge_inventory_{timestamp}.csv'
        df.to_csv(csv_filename, index=False)
        logger.info(f"Saved gauge inventory to {csv_filename}")
        
        # Save analysis report JSON
        json_filename = f'gauge_analysis_report_{timestamp}.json'
        with open(json_filename, 'w') as f:
            json.dump(reports, f, indent=2, default=str)
        logger.info(f"Saved analysis report to {json_filename}")
        
        return csv_filename, json_filename

def main():
    """Main execution function"""
    # Initialize analyzer
    analyzer = PakistanGaugeAnalyzer()
    
    # Analyze gauges
    df = analyzer.analyze_all_gauges()
    
    # Generate reports
    reports = analyzer.generate_reports(df)
    
    # Print summary
    print("\n=== Pakistan Gauge Analysis Summary ===")
    print(f"Total gauges analyzed: {len(df)}")
    print("\nClassification breakdown:")
    for classification, count in reports['classification_summary'].items():
        print(f"  {classification}: {count}")
    
    print("\nSource breakdown:")
    for source, count in reports['source_summary'].items():
        print(f"  {source}: {count}")
    
    # Save results
    csv_file, json_file = analyzer.save_results(df, reports)
    
    print(f"\nResults saved to:")
    print(f"  - {csv_file}")
    print(f"  - {json_file}")

if __name__ == "__main__":
    main()