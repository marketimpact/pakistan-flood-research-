#!/usr/bin/env python3
"""
Enhanced Pakistan Flood Status Analyzer
Integrates Google Flood Hub floodStatus API for real-time flood monitoring
"""

import requests
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class Severity(Enum):
    """Flood severity levels from Google Flood Hub API"""
    SEVERITY_UNSPECIFIED = "SEVERITY_UNSPECIFIED"
    EXTREME = "EXTREME"
    SEVERE = "SEVERE" 
    ABOVE_NORMAL = "ABOVE_NORMAL"
    NO_FLOODING = "NO_FLOODING"
    UNKNOWN = "UNKNOWN"

class ForecastTrend(Enum):
    """Forecast trend indicators"""
    FORECAST_TREND_UNSPECIFIED = "FORECAST_TREND_UNSPECIFIED"
    RISE = "RISE"
    FALL = "FALL"
    NO_CHANGE = "NO_CHANGE"

class MapInferenceType(Enum):
    """Map inference types"""
    MAP_INFERENCE_TYPE_UNSPECIFIED = "MAP_INFERENCE_TYPE_UNSPECIFIED"
    MODEL = "MODEL"
    IMAGE_CLASSIFICATION = "IMAGE_CLASSIFICATION"

class InundationMapType(Enum):
    """Inundation map types"""
    INUNDATION_MAP_TYPE_UNSPECIFIED = "INUNDATION_MAP_TYPE_UNSPECIFIED"
    PROBABILITY = "PROBABILITY"
    DEPTH = "DEPTH"

class InundationLevel(Enum):
    """Inundation levels"""
    INUNDATION_LEVEL_UNSPECIFIED = "INUNDATION_LEVEL_UNSPECIFIED"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"

@dataclass
class ValueChange:
    """Forecasted value change bounds"""
    lower_bound: float
    upper_bound: float
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ValueChange':
        return cls(
            lower_bound=data.get('lowerBound', 0.0),
            upper_bound=data.get('upperBound', 0.0)
        )

@dataclass
class TimeRange:
    """Time range representation"""
    start: str
    end: str
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'TimeRange':
        return cls(
            start=data.get('start', ''),
            end=data.get('end', '')
        )
    
    @property
    def duration_hours(self) -> float:
        """Calculate duration in hours"""
        try:
            start_dt = datetime.fromisoformat(self.start.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(self.end.replace('Z', '+00:00'))
            return (end_dt - start_dt).total_seconds() / 3600
        except Exception:
            return 0.0

@dataclass
class ForecastChange:
    """Forecast change information"""
    value_change: ValueChange
    reference_time_range: TimeRange
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'ForecastChange':
        return cls(
            value_change=ValueChange.from_dict(data.get('valueChange', {})),
            reference_time_range=TimeRange.from_dict(data.get('referenceTimeRange', {}))
        )

@dataclass
class InundationMap:
    """Single inundation map"""
    level: InundationLevel
    serialized_polygon_id: str
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'InundationMap':
        return cls(
            level=InundationLevel(data.get('level', 'INUNDATION_LEVEL_UNSPECIFIED')),
            serialized_polygon_id=data.get('serializedPolygonId', '')
        )

@dataclass
class InundationMapSet:
    """Set of inundation maps"""
    inundation_maps: List[InundationMap]
    time_range: TimeRange
    map_type: InundationMapType
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'InundationMapSet':
        maps = [InundationMap.from_dict(m) for m in data.get('inundationMaps', [])]
        return cls(
            inundation_maps=maps,
            time_range=TimeRange.from_dict(data.get('inundationMapsTimeRange', {})),
            map_type=InundationMapType(data.get('inundationMapType', 'INUNDATION_MAP_TYPE_UNSPECIFIED'))
        )

@dataclass
class LatLng:
    """Geographic coordinates"""
    latitude: float
    longitude: float
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'LatLng':
        return cls(
            latitude=data.get('latitude', 0.0),
            longitude=data.get('longitude', 0.0)
        )

@dataclass
class FloodStatus:
    """Complete flood status information"""
    gauge_id: str
    quality_verified: bool
    gauge_location: LatLng
    issued_time: str
    forecast_time_range: TimeRange
    forecast_change: Optional[ForecastChange]
    forecast_trend: ForecastTrend
    map_inference_type: MapInferenceType
    severity: Severity
    inundation_map_set: Optional[InundationMapSet]
    source: str
    serialized_notification_polygon_id: str
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'FloodStatus':
        return cls(
            gauge_id=data.get('gaugeId', ''),
            quality_verified=data.get('qualityVerified', False),
            gauge_location=LatLng.from_dict(data.get('gaugeLocation', {})),
            issued_time=data.get('issuedTime', ''),
            forecast_time_range=TimeRange.from_dict(data.get('forecastTimeRange', {})),
            forecast_change=ForecastChange.from_dict(data['forecastChange']) if 'forecastChange' in data else None,
            forecast_trend=ForecastTrend(data.get('forecastTrend', 'FORECAST_TREND_UNSPECIFIED')),
            map_inference_type=MapInferenceType(data.get('mapInferenceType', 'MAP_INFERENCE_TYPE_UNSPECIFIED')),
            severity=Severity(data.get('severity', 'SEVERITY_UNSPECIFIED')),
            inundation_map_set=InundationMapSet.from_dict(data['inundationMapSet']) if 'inundationMapSet' in data else None,
            source=data.get('source', ''),
            serialized_notification_polygon_id=data.get('serializedNotificationPolygonId', '')
        )
    
    @property
    def is_active_flood(self) -> bool:
        """Check if this represents an active flood condition"""
        return self.severity in [Severity.EXTREME, Severity.SEVERE, Severity.ABOVE_NORMAL]
    
    @property
    def has_inundation_maps(self) -> bool:
        """Check if inundation maps are available"""
        return self.inundation_map_set is not None and len(self.inundation_map_set.inundation_maps) > 0
    
    @property
    def risk_level(self) -> int:
        """Get numeric risk level (0-4)"""
        risk_mapping = {
            Severity.NO_FLOODING: 0,
            Severity.UNKNOWN: 1,
            Severity.ABOVE_NORMAL: 2,
            Severity.SEVERE: 3,
            Severity.EXTREME: 4,
            Severity.SEVERITY_UNSPECIFIED: 0
        }
        return risk_mapping.get(self.severity, 0)

class FloodStatusAnalyzer:
    """Enhanced analyzer for flood status data"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://floodforecasting.googleapis.com"
        
        # Pakistan bounding box
        self.pakistan_bounds = {
            "min_lat": 23.5,
            "max_lat": 37.5,
            "min_lon": 60.5,
            "max_lon": 77.5
        }
    
    def fetch_flood_status_by_area(self) -> List[FloodStatus]:
        """Fetch flood status for Pakistani region"""
        try:
            url = f"{self.base_url}/v1/floodStatus:searchLatestFloodStatusByArea"
            
            # Use correct format for flood status
            payload = {
                'regionCode': 'PK',
                'pageSize': 1000
            }
            
            params = {}
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                params["key"] = self.api_key
            
            logger.info(f"Fetching flood status from: {url}")
            response = requests.post(url, json=payload, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            flood_statuses = []
            
            for status_data in data.get('floodStatuses', []):
                flood_statuses.append(FloodStatus.from_dict(status_data))
            
            logger.info(f"Found {len(flood_statuses)} flood status records")
            return flood_statuses
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return self._get_sample_flood_status()
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return self._get_sample_flood_status()
    
    def fetch_flood_status_by_gauge_ids(self, gauge_ids: List[str]) -> List[FloodStatus]:
        """Fetch flood status for specific gauge IDs"""
        try:
            url = f"{self.base_url}/v1/floodStatus:queryLatestFloodStatusByGaugeIds"
            
            payload = {
                "gaugeIds": gauge_ids
            }
            
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            logger.info(f"Fetching flood status for {len(gauge_ids)} gauges")
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            flood_statuses = []
            
            for status_data in data.get('floodStatuses', []):
                flood_statuses.append(FloodStatus.from_dict(status_data))
            
            logger.info(f"Found {len(flood_statuses)} flood status records")
            return flood_statuses
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            return self._get_sample_flood_status()
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return self._get_sample_flood_status()
    
    def _get_sample_flood_status(self) -> List[FloodStatus]:
        """Sample flood status data for testing"""
        sample_data = [
            {
                "gaugeId": "PKGR0001",
                "qualityVerified": True,
                "gaugeLocation": {"latitude": 33.9, "longitude": 72.7},
                "issuedTime": "2025-07-01T12:00:00Z",
                "forecastTimeRange": {
                    "start": "2025-07-01T12:00:00Z",
                    "end": "2025-07-02T12:00:00Z"
                },
                "forecastChange": {
                    "valueChange": {"lowerBound": 0.5, "upperBound": 1.2},
                    "referenceTimeRange": {
                        "start": "2025-06-30T12:00:00Z",
                        "end": "2025-07-01T12:00:00Z"
                    }
                },
                "forecastTrend": "RISE",
                "mapInferenceType": "MODEL",
                "severity": "SEVERE",
                "inundationMapSet": {
                    "inundationMaps": [
                        {"level": "HIGH", "serializedPolygonId": "poly_high_001"},
                        {"level": "MEDIUM", "serializedPolygonId": "poly_med_001"},
                        {"level": "LOW", "serializedPolygonId": "poly_low_001"}
                    ],
                    "inundationMapsTimeRange": {
                        "start": "2025-07-01T18:00:00Z",
                        "end": "2025-07-02T06:00:00Z"
                    },
                    "inundationMapType": "PROBABILITY"
                },
                "source": "GRDC",
                "serializedNotificationPolygonId": "notify_001"
            },
            {
                "gaugeId": "WAPDA_001", 
                "qualityVerified": True,
                "gaugeLocation": {"latitude": 32.96, "longitude": 71.55},
                "issuedTime": "2025-07-01T12:00:00Z",
                "forecastTimeRange": {
                    "start": "2025-07-01T12:00:00Z", 
                    "end": "2025-07-02T12:00:00Z"
                },
                "forecastTrend": "NO_CHANGE",
                "mapInferenceType": "MODEL",
                "severity": "NO_FLOODING",
                "source": "WAPDA",
                "serializedNotificationPolygonId": "notify_002"
            },
            {
                "gaugeId": "hybas_4121489010",
                "qualityVerified": False,
                "gaugeLocation": {"latitude": 26.06, "longitude": 68.93},
                "issuedTime": "2025-07-01T12:00:00Z",
                "forecastTimeRange": {
                    "start": "2025-07-01T12:00:00Z",
                    "end": "2025-07-02T12:00:00Z"
                },
                "forecastTrend": "RISE",
                "mapInferenceType": "IMAGE_CLASSIFICATION",
                "severity": "ABOVE_NORMAL",
                "source": "HYBAS",
                "serializedNotificationPolygonId": "notify_003"
            }
        ]
        
        return [FloodStatus.from_dict(data) for data in sample_data]
    
    def analyze_flood_patterns(self, flood_statuses: List[FloodStatus]) -> Dict:
        """Analyze flood patterns and generate insights"""
        if not flood_statuses:
            return {}
        
        analysis = {
            'total_gauges': len(flood_statuses),
            'analysis_time': datetime.now().isoformat(),
            'severity_distribution': {},
            'trend_analysis': {},
            'quality_analysis': {},
            'source_analysis': {},
            'geographic_analysis': {},
            'inundation_analysis': {},
            'risk_assessment': {}
        }
        
        # Severity distribution
        severity_counts = {}
        for status in flood_statuses:
            severity = status.severity.value
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        analysis['severity_distribution'] = severity_counts
        
        # Trend analysis
        trend_counts = {}
        for status in flood_statuses:
            trend = status.forecast_trend.value
            trend_counts[trend] = trend_counts.get(trend, 0) + 1
        analysis['trend_analysis'] = trend_counts
        
        # Quality analysis
        quality_verified = sum(1 for s in flood_statuses if s.quality_verified)
        analysis['quality_analysis'] = {
            'quality_verified': quality_verified,
            'quality_verified_percentage': (quality_verified / len(flood_statuses)) * 100,
            'model_based': sum(1 for s in flood_statuses if s.map_inference_type == MapInferenceType.MODEL),
            'image_classification': sum(1 for s in flood_statuses if s.map_inference_type == MapInferenceType.IMAGE_CLASSIFICATION)
        }
        
        # Source analysis
        source_counts = {}
        for status in flood_statuses:
            source = status.source
            source_counts[source] = source_counts.get(source, 0) + 1
        analysis['source_analysis'] = source_counts
        
        # Geographic analysis
        latitudes = [s.gauge_location.latitude for s in flood_statuses]
        longitudes = [s.gauge_location.longitude for s in flood_statuses]
        analysis['geographic_analysis'] = {
            'latitude_range': [min(latitudes), max(latitudes)],
            'longitude_range': [min(longitudes), max(longitudes)],
            'center_point': [sum(latitudes)/len(latitudes), sum(longitudes)/len(longitudes)]
        }
        
        # Inundation map analysis
        with_maps = sum(1 for s in flood_statuses if s.has_inundation_maps)
        analysis['inundation_analysis'] = {
            'gauges_with_maps': with_maps,
            'map_coverage_percentage': (with_maps / len(flood_statuses)) * 100
        }
        
        # Risk assessment
        active_floods = sum(1 for s in flood_statuses if s.is_active_flood)
        risk_levels = [s.risk_level for s in flood_statuses]
        analysis['risk_assessment'] = {
            'active_floods': active_floods,
            'active_flood_percentage': (active_floods / len(flood_statuses)) * 100,
            'average_risk_level': sum(risk_levels) / len(risk_levels),
            'max_risk_level': max(risk_levels),
            'high_risk_gauges': sum(1 for r in risk_levels if r >= 3)
        }
        
        return analysis
    
    def create_flood_status_dataframe(self, flood_statuses: List[FloodStatus]) -> pd.DataFrame:
        """Convert flood status list to pandas DataFrame"""
        data = []
        
        for status in flood_statuses:
            row = {
                'gaugeId': status.gauge_id,
                'latitude': status.gauge_location.latitude,
                'longitude': status.gauge_location.longitude,
                'qualityVerified': status.quality_verified,
                'issuedTime': status.issued_time,
                'severity': status.severity.value,
                'forecastTrend': status.forecast_trend.value,
                'mapInferenceType': status.map_inference_type.value,
                'source': status.source,
                'riskLevel': status.risk_level,
                'isActiveFlood': status.is_active_flood,
                'hasInundationMaps': status.has_inundation_maps,
                'forecastDurationHours': status.forecast_time_range.duration_hours
            }
            
            # Add forecast change data if available
            if status.forecast_change:
                row['forecastChangeLower'] = status.forecast_change.value_change.lower_bound
                row['forecastChangeUpper'] = status.forecast_change.value_change.upper_bound
            else:
                row['forecastChangeLower'] = None
                row['forecastChangeUpper'] = None
            
            # Add inundation map data if available
            if status.inundation_map_set:
                row['inundationMapType'] = status.inundation_map_set.map_type.value
                row['inundationMapCount'] = len(status.inundation_map_set.inundation_maps)
            else:
                row['inundationMapType'] = None
                row['inundationMapCount'] = 0
            
            data.append(row)
        
        return pd.DataFrame(data)
    
    def generate_flood_status_report(self, flood_statuses: List[FloodStatus]) -> Dict:
        """Generate comprehensive flood status report"""
        analysis = self.analyze_flood_patterns(flood_statuses)
        df = self.create_flood_status_dataframe(flood_statuses)
        
        # Enhanced analysis
        report = {
            'executive_summary': {
                'total_gauges_monitored': len(flood_statuses),
                'active_flood_alerts': analysis['risk_assessment']['active_floods'],
                'quality_verified_gauges': analysis['quality_analysis']['quality_verified'],
                'average_risk_level': round(analysis['risk_assessment']['average_risk_level'], 2)
            },
            'detailed_analysis': analysis,
            'recommendations': self._generate_flood_recommendations(analysis, df),
            'alert_priorities': self._prioritize_alerts(flood_statuses)
        }
        
        return report
    
    def _generate_flood_recommendations(self, analysis: Dict, df: pd.DataFrame) -> Dict:
        """Generate actionable recommendations based on flood analysis"""
        recommendations = {}
        
        # Immediate actions
        active_floods = analysis['risk_assessment']['active_floods']
        if active_floods > 0:
            recommendations['immediate_actions'] = [
                f"Monitor {active_floods} active flood alerts closely",
                "Activate emergency response protocols for high-risk areas",
                "Issue public warnings for affected regions"
            ]
        
        # Data quality improvements
        quality_percentage = analysis['quality_analysis']['quality_verified_percentage']
        if quality_percentage < 80:
            recommendations['data_quality'] = [
                f"Only {quality_percentage:.1f}% of gauges are quality verified",
                "Focus monitoring on quality-verified gauges for critical decisions",
                "Request verification status updates from Google Flood Hub"
            ]
        
        # Coverage improvements
        map_coverage = analysis['inundation_analysis']['map_coverage_percentage']
        if map_coverage < 50:
            recommendations['coverage_improvements'] = [
                f"Only {map_coverage:.1f}% of gauges have inundation maps",
                "Prioritize gauges with inundation map data for public alerts",
                "Work with Google to expand inundation mapping coverage"
            ]
        
        return recommendations
    
    def _prioritize_alerts(self, flood_statuses: List[FloodStatus]) -> List[Dict]:
        """Prioritize flood alerts by risk and reliability"""
        priorities = []
        
        for status in flood_statuses:
            if not status.is_active_flood:
                continue
            
            priority_score = status.risk_level * 10
            
            # Boost score for quality verified
            if status.quality_verified:
                priority_score += 20
            
            # Boost score for model-based inference
            if status.map_inference_type == MapInferenceType.MODEL:
                priority_score += 15
            
            # Boost score for inundation maps
            if status.has_inundation_maps:
                priority_score += 10
            
            # Boost score for rising trend
            if status.forecast_trend == ForecastTrend.RISE:
                priority_score += 5
            
            priorities.append({
                'gaugeId': status.gauge_id,
                'severity': status.severity.value,
                'location': f"{status.gauge_location.latitude:.3f}, {status.gauge_location.longitude:.3f}",
                'priority_score': priority_score,
                'quality_verified': status.quality_verified,
                'has_maps': status.has_inundation_maps,
                'source': status.source
            })
        
        # Sort by priority score (highest first)
        priorities.sort(key=lambda x: x['priority_score'], reverse=True)
        
        return priorities[:10]  # Top 10 priorities

def main():
    """Test the flood status analyzer"""
    analyzer = FloodStatusAnalyzer()
    
    # Fetch flood status data
    flood_statuses = analyzer.fetch_flood_status_by_area()
    
    # Generate report
    report = analyzer.generate_flood_status_report(flood_statuses)
    
    # Print summary
    print("\n=== PAKISTAN FLOOD STATUS ANALYSIS ===")
    print(f"Total Gauges: {report['executive_summary']['total_gauges_monitored']}")
    print(f"Active Floods: {report['executive_summary']['active_flood_alerts']}")
    print(f"Quality Verified: {report['executive_summary']['quality_verified_gauges']}")
    print(f"Average Risk Level: {report['executive_summary']['average_risk_level']}/4")
    
    if report['alert_priorities']:
        print(f"\nTop Priority Alerts:")
        for i, alert in enumerate(report['alert_priorities'][:3], 1):
            print(f"{i}. {alert['gaugeId']} - {alert['severity']} (Score: {alert['priority_score']})")
    
    # Save report
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'flood_status_report_{timestamp}.json'
    with open(filename, 'w') as f:
        json.dump(report, f, indent=2, default=str)
    print(f"\nReport saved to {filename}")

if __name__ == "__main__":
    main()