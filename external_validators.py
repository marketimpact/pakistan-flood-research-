#!/usr/bin/env python3
"""
External Validation Module for Pakistani Gauge Data
Cross-references Google Flood Hub data with Pakistani government sources
"""

import requests
import pandas as pd
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from geopy.distance import geodesic
import logging

logger = logging.getLogger(__name__)

@dataclass
class ExternalStation:
    """Data structure for external station references"""
    name: str
    latitude: float
    longitude: float
    source: str
    river: str = ""
    station_code: str = ""
    operational: bool = True

class ExternalValidationService:
    """Service for validating gauges against external Pakistani data sources"""
    
    def __init__(self):
        self.wapda_stations = self._load_wapda_stations()
        self.ffd_stations = self._load_ffd_stations()
        self.pmd_stations = self._load_pmd_stations()
        self.ndma_stations = self._load_ndma_stations()
    
    def _load_wapda_stations(self) -> List[ExternalStation]:
        """Load known WAPDA (Water and Power Development Authority) stations"""
        # Known major WAPDA stations with coordinates
        wapda_data = [
            # Indus River System
            {"name": "Tarbela Dam", "lat": 33.9, "lon": 72.7, "river": "Indus", "code": "TARBELA"},
            {"name": "Kalabagh", "lat": 32.96, "lon": 71.55, "river": "Indus", "code": "KALABAGH"},
            {"name": "Chashma Barrage", "lat": 32.45, "lon": 71.35, "river": "Indus", "code": "CHASHMA"},
            {"name": "Sukkur Barrage", "lat": 27.7, "lon": 68.85, "river": "Indus", "code": "SUKKUR"},
            {"name": "Kotri Barrage", "lat": 25.37, "lon": 68.31, "river": "Indus", "code": "KOTRI"},
            
            # Chenab River System
            {"name": "Marala Headworks", "lat": 32.67, "lon": 74.46, "river": "Chenab", "code": "MARALA"},
            {"name": "Khanki Headworks", "lat": 31.30, "lon": 73.58, "river": "Chenab", "code": "KHANKI"},
            {"name": "Qadirabad Barrage", "lat": 31.40, "lon": 73.52, "river": "Chenab", "code": "QADIRABAD"},
            
            # Jhelum River System
            {"name": "Mangla Dam", "lat": 33.13, "lon": 73.64, "river": "Jhelum", "code": "MANGLA"},
            {"name": "Rasul Barrage", "lat": 31.36, "lon": 73.52, "river": "Jhelum", "code": "RASUL"},
            
            # Ravi River System
            {"name": "Jassar Barrage", "lat": 31.05, "lon": 73.92, "river": "Ravi", "code": "JASSAR"},
            {"name": "Balloki Headworks", "lat": 31.22, "lon": 73.72, "river": "Ravi", "code": "BALLOKI"},
            
            # Sutlej River System
            {"name": "Sulemanki Headworks", "lat": 30.07, "lon": 73.07, "river": "Sutlej", "code": "SULEMANKI"},
            {"name": "Islam Headworks", "lat": 30.92, "lon": 72.18, "river": "Sutlej", "code": "ISLAM"},
            
            # Kabul River System
            {"name": "Warsak Dam", "lat": 34.15, "lon": 71.4, "river": "Kabul", "code": "WARSAK"},
            
            # Kurram River
            {"name": "Kurram Tangi Dam", "lat": 33.77, "lon": 69.95, "river": "Kurram", "code": "KURRAM"}
        ]
        
        return [
            ExternalStation(
                name=station["name"],
                latitude=station["lat"],
                longitude=station["lon"],
                source="WAPDA",
                river=station["river"],
                station_code=station["code"]
            ) for station in wapda_data
        ]
    
    def _load_ffd_stations(self) -> List[ExternalStation]:
        """Load Federal Flood Division (FFD) monitoring stations"""
        # FFD operates additional monitoring points beyond major barrages
        ffd_data = [
            # Additional Indus monitoring points
            {"name": "Attock", "lat": 33.77, "lon": 72.36, "river": "Indus", "code": "FFD_ATTOCK"},
            {"name": "Nowshera", "lat": 34.02, "lon": 71.98, "river": "Kabul", "code": "FFD_NOWSHERA"},
            {"name": "Kuram Garhi", "lat": 32.58, "lon": 71.13, "river": "Indus", "code": "FFD_KURAM"},
            
            # Chitral region
            {"name": "Chitral", "lat": 35.85, "lon": 71.79, "river": "Chitral", "code": "FFD_CHITRAL"},
            
            # Balochistan monitoring
            {"name": "Zhob", "lat": 31.34, "lon": 69.45, "river": "Zhob", "code": "FFD_ZHOB"},
            {"name": "Sibi", "lat": 29.54, "lon": 67.88, "river": "Nari", "code": "FFD_SIBI"},
            
            # Punjab tributaries
            {"name": "Trimmu", "lat": 31.05, "lon": 72.18, "river": "Chenab", "code": "FFD_TRIMMU"},
            {"name": "Sidhnai", "lat": 30.67, "lon": 72.92, "river": "Ravi", "code": "FFD_SIDHNAI"}
        ]
        
        return [
            ExternalStation(
                name=station["name"],
                latitude=station["lat"],
                longitude=station["lon"],
                source="FFD",
                river=station["river"],
                station_code=station["code"]
            ) for station in ffd_data
        ]
    
    def _load_pmd_stations(self) -> List[ExternalStation]:
        """Load Pakistan Meteorological Department (PMD) hydro stations"""
        # PMD operates meteorological and hydrological monitoring
        pmd_data = [
            {"name": "Peshawar", "lat": 34.02, "lon": 71.53, "river": "Kabul", "code": "PMD_PESHAWAR"},
            {"name": "Lahore", "lat": 31.55, "lon": 74.35, "river": "Ravi", "code": "PMD_LAHORE"},
            {"name": "Multan", "lat": 30.20, "lon": 71.45, "river": "Chenab", "code": "PMD_MULTAN"},
            {"name": "Hyderabad", "lat": 25.37, "lon": 68.37, "river": "Indus", "code": "PMD_HYDERABAD"},
            {"name": "Karachi", "lat": 24.86, "lon": 67.01, "river": "Hub", "code": "PMD_KARACHI"},
            {"name": "Quetta", "lat": 30.18, "lon": 66.98, "river": "Hab", "code": "PMD_QUETTA"},
            {"name": "Gilgit", "lat": 35.92, "lon": 74.31, "river": "Gilgit", "code": "PMD_GILGIT"},
            {"name": "Skardu", "lat": 35.30, "lon": 75.63, "river": "Indus", "code": "PMD_SKARDU"}
        ]
        
        return [
            ExternalStation(
                name=station["name"],
                latitude=station["lat"],
                longitude=station["lon"],
                source="PMD",
                river=station["river"],
                station_code=station["code"]
            ) for station in pmd_data
        ]
    
    def _load_ndma_stations(self) -> List[ExternalStation]:
        """Load National Disaster Management Authority (NDMA) reference points"""
        # NDMA monitoring points for disaster management
        ndma_data = [
            {"name": "Muzaffarabad", "lat": 34.37, "lon": 73.47, "river": "Jhelum", "code": "NDMA_MZD"},
            {"name": "Mithi", "lat": 24.74, "lon": 69.78, "river": "Rann", "code": "NDMA_MITHI"},
            {"name": "Jacobabad", "lat": 28.28, "lon": 68.44, "river": "Indus", "code": "NDMA_JACOB"},
            {"name": "DI Khan", "lat": 31.83, "lon": 70.90, "river": "Indus", "code": "NDMA_DIKAN"},
            {"name": "Bannu", "lat": 32.99, "lon": 70.60, "river": "Kurram", "code": "NDMA_BANNU"}
        ]
        
        return [
            ExternalStation(
                name=station["name"],
                latitude=station["lat"],
                longitude=station["lon"],
                source="NDMA",
                river=station["river"],
                station_code=station["code"]
            ) for station in ndma_data
        ]
    
    def find_matching_stations(self, gauge_lat: float, gauge_lon: float, 
                             tolerance_km: float = 1.0) -> List[Dict]:
        """Find external stations within tolerance distance of gauge coordinates"""
        matches = []
        gauge_coords = (gauge_lat, gauge_lon)
        
        # Check all external station sources
        all_stations = (self.wapda_stations + self.ffd_stations + 
                       self.pmd_stations + self.ndma_stations)
        
        for station in all_stations:
            try:
                station_coords = (station.latitude, station.longitude)
                distance = geodesic(gauge_coords, station_coords).kilometers
                
                if distance <= tolerance_km:
                    matches.append({
                        'station_name': station.name,
                        'source': station.source,
                        'river': station.river,
                        'station_code': station.station_code,
                        'distance_km': distance,
                        'coordinates': (station.latitude, station.longitude)
                    })
            except Exception as e:
                logger.warning(f"Error calculating distance for {station.name}: {e}")
                continue
        
        # Sort by distance
        matches.sort(key=lambda x: x['distance_km'])
        return matches
    
    def validate_gauge_against_external(self, gauge_data: Dict) -> Dict:
        """Validate a single gauge against external Pakistani data sources"""
        location = gauge_data.get('location', {})
        if not location or 'latitude' not in location or 'longitude' not in location:
            return {
                'validation_status': 'no_coordinates',
                'matches': [],
                'confidence_boost': 0,
                'evidence': ['No coordinates available for validation']
            }
        
        lat = location['latitude']
        lon = location['longitude']
        
        # Find matches with different tolerance levels
        exact_matches = self.find_matching_stations(lat, lon, tolerance_km=0.5)
        close_matches = self.find_matching_stations(lat, lon, tolerance_km=1.0)
        nearby_matches = self.find_matching_stations(lat, lon, tolerance_km=5.0)
        
        # Determine validation status and confidence boost
        confidence_boost = 0
        evidence = []
        
        if exact_matches:
            validation_status = 'exact_match'
            confidence_boost = 40
            evidence.append(f"Exact match with {exact_matches[0]['station_name']}")
        elif close_matches:
            validation_status = 'close_match'
            confidence_boost = 25
            evidence.append(f"Close match with {close_matches[0]['station_name']} ({close_matches[0]['distance_km']:.2f}km)")
        elif nearby_matches:
            validation_status = 'nearby_match'
            confidence_boost = 10
            evidence.append(f"Nearby station: {nearby_matches[0]['station_name']} ({nearby_matches[0]['distance_km']:.2f}km)")
        else:
            validation_status = 'no_match'
            confidence_boost = 0
            evidence.append('No external station matches found')
        
        return {
            'validation_status': validation_status,
            'matches': exact_matches + close_matches + nearby_matches,
            'confidence_boost': confidence_boost,
            'evidence': evidence
        }
    
    def get_all_external_stations(self) -> pd.DataFrame:
        """Get DataFrame of all known external stations"""
        all_stations = (self.wapda_stations + self.ffd_stations + 
                       self.pmd_stations + self.ndma_stations)
        
        df_data = []
        for station in all_stations:
            df_data.append({
                'name': station.name,
                'latitude': station.latitude,
                'longitude': station.longitude,
                'source': station.source,
                'river': station.river,
                'station_code': station.station_code,
                'operational': station.operational
            })
        
        return pd.DataFrame(df_data)
    
    def generate_coverage_report(self, gauge_df: pd.DataFrame) -> Dict:
        """Generate a report on external validation coverage"""
        total_gauges = len(gauge_df)
        
        # Count validation results
        validation_counts = {
            'exact_match': 0,
            'close_match': 0,
            'nearby_match': 0,
            'no_match': 0,
            'no_coordinates': 0
        }
        
        # This would be called after validation is performed
        # For now, return structure for future implementation
        
        external_df = self.get_all_external_stations()
        
        return {
            'total_external_stations': len(external_df),
            'external_by_source': external_df['source'].value_counts().to_dict(),
            'external_by_river': external_df['river'].value_counts().to_dict(),
            'validation_coverage': validation_counts,
            'coverage_percentage': 0  # To be calculated after validation
        }

# Usage example and test function
def test_validation_service():
    """Test the external validation service"""
    validator = ExternalValidationService()
    
    # Test with sample gauge data
    sample_gauge = {
        'gaugeId': 'TEST_001',
        'location': {'latitude': 33.9, 'longitude': 72.7}  # Near Tarbela
    }
    
    result = validator.validate_gauge_against_external(sample_gauge)
    print("Validation result:", result)
    
    # Get all external stations
    external_df = validator.get_all_external_stations()
    print(f"\nTotal external stations: {len(external_df)}")
    print("\nBy source:")
    print(external_df['source'].value_counts())

if __name__ == "__main__":
    test_validation_service()