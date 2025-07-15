#!/usr/bin/env python3
"""
Comprehensive Pakistan Flood Hub Analyzer
Integrates gauges, gaugeModels, and floodStatus APIs for complete flood monitoring
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
# Removed unused async imports

from gauge_analyzer import PakistanGaugeAnalyzer, GaugeClassification
from external_validators import ExternalValidationService
from flood_status_analyzer import FloodStatusAnalyzer, FloodStatus, Severity
from config import config

logger = logging.getLogger(__name__)

class GaugeValueUnit(Enum):
    """Gauge value units from API"""
    GAUGE_VALUE_UNIT_UNSPECIFIED = "GAUGE_VALUE_UNIT_UNSPECIFIED"
    METERS = "METERS"
    CUBIC_METERS_PER_SECOND = "CUBIC_METERS_PER_SECOND"

@dataclass
class Thresholds:
    """Gauge threshold levels"""
    warning_level: float
    danger_level: float
    extreme_danger_level: Optional[float] = None
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Thresholds':
        return cls(
            warning_level=data.get('warningLevel', 0.0),
            danger_level=data.get('dangerLevel', 0.0),
            extreme_danger_level=data.get('extremeDangerLevel')
        )

@dataclass
class GaugeModel:
    """Gauge model metadata"""
    gauge_id: str
    gauge_model_id: str
    thresholds: Thresholds
    gauge_value_unit: GaugeValueUnit
    quality_verified: bool
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'GaugeModel':
        return cls(
            gauge_id=data.get('gaugeId', ''),
            gauge_model_id=data.get('gaugeModelId', ''),
            thresholds=Thresholds.from_dict(data.get('thresholds', {})),
            gauge_value_unit=GaugeValueUnit(data.get('gaugeValueUnit', 'GAUGE_VALUE_UNIT_UNSPECIFIED')),
            quality_verified=data.get('qualityVerified', False)
        )

@dataclass
class EnhancedGauge:
    """Enhanced gauge with all available data"""
    # Basic gauge info
    gauge_id: str
    location: Dict[str, float]
    site_name: str
    source: str
    river: str
    country_code: str
    quality_verified: bool
    has_model: bool
    
    # Classification data
    classification: str
    confidence_score: int
    evidence: List[str]
    external_validation: Dict
    
    # Model data (if available)
    gauge_model: Optional[GaugeModel] = None
    
    # Current flood status (if available)
    flood_status: Optional[FloodStatus] = None
    
    @property
    def is_reliable(self) -> bool:
        """Check if gauge is reliable for alerting"""
        return (
            self.quality_verified and
            self.classification in [GaugeClassification.VERIFIED_PHYSICAL, GaugeClassification.LIKELY_PHYSICAL] and
            self.confidence_score >= 70
        )
    
    @property
    def alert_priority(self) -> int:
        """Calculate alert priority (0-100)"""
        priority = 0
        
        # Base score from classification confidence
        priority += min(self.confidence_score, 50)
        
        # Quality verification bonus
        if self.quality_verified:
            priority += 20
        
        # Physical gauge bonus
        if self.classification == GaugeClassification.VERIFIED_PHYSICAL:
            priority += 15
        elif self.classification == GaugeClassification.LIKELY_PHYSICAL:
            priority += 10
        
        # Model availability bonus
        if self.has_model and self.gauge_model and self.gauge_model.quality_verified:
            priority += 10
        
        # Active flooding bonus
        if self.flood_status and self.flood_status.is_active_flood:
            priority += 15
            if self.flood_status.severity == Severity.EXTREME:
                priority += 10
        
        return min(priority, 100)

class ComprehensiveFloodAnalyzer:
    """Comprehensive analyzer integrating all Google Flood Hub APIs"""
    
    def __init__(self, api_key: Optional[str] = None):
        # Use provided API key or get from config
        self.api_key = api_key or config.api_key
        self.base_url = config.base_url
        
        # Initialize component analyzers
        self.gauge_analyzer = PakistanGaugeAnalyzer(self.api_key)
        self.validator = ExternalValidationService()
        self.flood_analyzer = FloodStatusAnalyzer(self.api_key)
        
        # Log API configuration status
        if self.api_key:
            logger.info(f"Using Google Flood Hub API key: {self.api_key[:10]}...")
        else:
            logger.warning("No API key configured - using sample data")
        
        # Pakistan bounding box
        self.pakistan_bounds = {
            "min_lat": 23.5,
            "max_lat": 37.5,
            "min_lon": 60.5,
            "max_lon": 77.5
        }
        
        self.enhanced_gauges = []
    
    def run_comprehensive_analysis(self) -> Dict:
        """Run complete analysis across all APIs"""
        logger.info("Starting comprehensive flood analysis...")
        
        # Step 1: Get all Pakistani gauges
        logger.info("Step 1: Fetching gauge metadata...")
        gauges_data = self._fetch_all_gauges()
        
        # Step 2: Classify gauges (physical vs virtual)
        logger.info("Step 2: Classifying gauges...")
        classified_gauges = self._classify_gauges(gauges_data)
        
        # Step 3: Get gauge models for gauges that have them
        logger.info("Step 3: Fetching gauge models...")
        gauges_with_models = self._fetch_gauge_models(classified_gauges)
        
        # Step 4: Get current flood status
        logger.info("Step 4: Fetching flood status...")
        complete_gauges = self._fetch_flood_status(gauges_with_models)
        
        # Step 5: Generate comprehensive analysis
        logger.info("Step 5: Generating comprehensive analysis...")
        analysis = self._generate_comprehensive_analysis(complete_gauges)
        
        # Step 6: Save results
        logger.info("Step 6: Saving results...")
        file_paths = self._save_comprehensive_results(complete_gauges, analysis)
        
        return {
            'enhanced_gauges': complete_gauges,
            'analysis': analysis,
            'file_paths': file_paths
        }
    
    def _fetch_all_gauges(self) -> List[Dict]:
        """Fetch all gauge metadata from Pakistan region"""
        try:
            url = f"{self.base_url}/v1/gauges:searchGaugesByArea"
            
            # Use correct request format for Pakistan
            payload = {
                'regionCode': 'PK',  # Pakistan ISO code
                'includeNonQualityVerified': True,
                'includeGaugesWithoutHydroModel': True,
                'pageSize': 50000  # Maximum allowed
            }
            
            params = {}
            headers = {"Content-Type": "application/json"}
            
            if self.api_key:
                params["key"] = self.api_key
            
            logger.info(f"Fetching gauges from: {url}")
            response = requests.post(url, json=payload, params=params, headers=headers, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            gauges = data.get('gauges', [])
            
            logger.info(f"Found {len(gauges)} gauges in Pakistan")
            return gauges
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Gauges API request failed: {e}")
            return self._get_sample_gauges()
        except json.JSONDecodeError as e:
            logger.error(f"JSON decode error: {e}")
            return self._get_sample_gauges()
    
    def _get_sample_gauges(self) -> List[Dict]:
        """Sample gauge data matching API specification"""
        return [
            {
                "gaugeId": "PKGR0001",
                "location": {"latitude": 33.9, "longitude": 72.7},
                "siteName": "Tarbela Dam",
                "source": "GRDC",
                "river": "Indus River",
                "countryCode": "PK",
                "qualityVerified": True,
                "hasModel": True
            },
            {
                "gaugeId": "hybas_4121489010",
                "location": {"latitude": 26.060416666665333, "longitude": 68.931249999995941},
                "siteName": "",
                "source": "HYBAS",
                "river": "",
                "countryCode": "PK",
                "qualityVerified": True,
                "hasModel": True
            },
            {
                "gaugeId": "WAPDA_001",
                "location": {"latitude": 32.96, "longitude": 71.55},
                "siteName": "Kalabagh Barrage",
                "source": "WAPDA",
                "river": "Indus River",
                "countryCode": "PK",
                "qualityVerified": True,
                "hasModel": True
            }
        ]
    
    def _classify_gauges(self, gauges_data: List[Dict]) -> List[EnhancedGauge]:
        """Classify gauges using existing classification system"""
        enhanced_gauges = []
        
        for gauge_data in gauges_data:
            # Use existing classification logic
            gauge_info = self.gauge_analyzer.analyze_gauge_physicality(gauge_data)
            
            # Add external validation
            validation = self.validator.validate_gauge_against_external(gauge_data)
            
            # Create enhanced gauge
            enhanced = EnhancedGauge(
                gauge_id=gauge_data.get('gaugeId', ''),
                location=gauge_data.get('location', {}),
                site_name=gauge_data.get('siteName', ''),
                source=gauge_data.get('source', ''),
                river=gauge_data.get('river', ''),
                country_code=gauge_data.get('countryCode', ''),
                quality_verified=gauge_data.get('qualityVerified', False),
                has_model=gauge_data.get('hasModel', False),
                classification=gauge_info.classification,
                confidence_score=gauge_info.confidence_score,
                evidence=gauge_info.evidence,
                external_validation=validation
            )
            
            enhanced_gauges.append(enhanced)
        
        return enhanced_gauges
    
    def _fetch_gauge_models(self, gauges: List[EnhancedGauge]) -> List[EnhancedGauge]:
        """Fetch gauge models for gauges that have them"""
        gauges_with_models = gauges[:]  # Copy list
        
        # Get gauge IDs that have models
        model_gauge_ids = [g.gauge_id for g in gauges if g.has_model]
        
        if not model_gauge_ids:
            return gauges_with_models
        
        try:
            url = f"{self.base_url}/v1/gaugeModels:batchGet"
            
            # Use correct format: names as query parameters
            names = [f"gaugeModels/{gauge_id}" for gauge_id in model_gauge_ids[:100]]  # Limit to 100 for testing
            params = {"names": names}
            if self.api_key:
                params["key"] = self.api_key
            
            logger.info(f"Fetching models for {len(names)} gauges")
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            gauge_models = {}
            
            for model_data in data.get('gaugeModels', []):
                model = GaugeModel.from_dict(model_data)
                gauge_models[model.gauge_id] = model
            
            # Add models to enhanced gauges
            for gauge in gauges_with_models:
                if gauge.gauge_id in gauge_models:
                    gauge.gauge_model = gauge_models[gauge.gauge_id]
            
            logger.info(f"Found models for {len(gauge_models)} gauges")
            
        except Exception as e:
            logger.error(f"Error fetching gauge models: {e}")
            # Add sample models for testing
            self._add_sample_models(gauges_with_models)
        
        return gauges_with_models
    
    def _add_sample_models(self, gauges: List[EnhancedGauge]):
        """Add sample models for testing"""
        sample_models = {
            "PKGR0001": {
                "gaugeId": "PKGR0001",
                "gaugeModelId": "model_001",
                "thresholds": {
                    "warningLevel": 5000.0,
                    "dangerLevel": 6000.0,
                    "extremeDangerLevel": 7000.0
                },
                "gaugeValueUnit": "CUBIC_METERS_PER_SECOND",
                "qualityVerified": True
            },
            "WAPDA_001": {
                "gaugeId": "WAPDA_001", 
                "gaugeModelId": "model_002",
                "thresholds": {
                    "warningLevel": 4500.0,
                    "dangerLevel": 5500.0,
                    "extremeDangerLevel": 6500.0
                },
                "gaugeValueUnit": "CUBIC_METERS_PER_SECOND",
                "qualityVerified": True
            }
        }
        
        for gauge in gauges:
            if gauge.gauge_id in sample_models:
                gauge.gauge_model = GaugeModel.from_dict(sample_models[gauge.gauge_id])
    
    def _fetch_flood_status(self, gauges: List[EnhancedGauge]) -> List[EnhancedGauge]:
        """Fetch current flood status for all gauges"""
        gauges_with_status = gauges[:]  # Copy list
        
        # Get all flood statuses for Pakistan region
        flood_statuses = self.flood_analyzer.fetch_flood_status_by_area()
        
        # Create mapping of gauge_id to flood status
        status_map = {status.gauge_id: status for status in flood_statuses}
        
        # Add flood status to gauges
        for gauge in gauges_with_status:
            if gauge.gauge_id in status_map:
                gauge.flood_status = status_map[gauge.gauge_id]
        
        logger.info(f"Found flood status for {len([g for g in gauges_with_status if g.flood_status])} gauges")
        return gauges_with_status
    
    def _generate_comprehensive_analysis(self, gauges: List[EnhancedGauge]) -> Dict:
        """Generate comprehensive analysis of all data"""
        analysis = {
            'summary': self._generate_summary_stats(gauges),
            'classification_analysis': self._analyze_classifications(gauges),
            'model_analysis': self._analyze_models(gauges),
            'flood_status_analysis': self._analyze_flood_status(gauges),
            'reliability_analysis': self._analyze_reliability(gauges),
            'priority_ranking': self._rank_gauges_by_priority(gauges),
            'recommendations': self._generate_system_recommendations(gauges),
            'coverage_analysis': self._analyze_coverage(gauges)
        }
        
        return analysis
    
    def _generate_summary_stats(self, gauges: List[EnhancedGauge]) -> Dict:
        """Generate summary statistics"""
        return {
            'total_gauges': len(gauges),
            'quality_verified': sum(1 for g in gauges if g.quality_verified),
            'with_models': sum(1 for g in gauges if g.has_model),
            'with_flood_status': sum(1 for g in gauges if g.flood_status),
            'reliable_gauges': sum(1 for g in gauges if g.is_reliable),
            'active_floods': sum(1 for g in gauges if g.flood_status and g.flood_status.is_active_flood),
            'analysis_timestamp': datetime.now().isoformat()
        }
    
    def _analyze_classifications(self, gauges: List[EnhancedGauge]) -> Dict:
        """Analyze gauge classifications"""
        classifications = {}
        confidence_scores = []
        
        for gauge in gauges:
            classifications[gauge.classification] = classifications.get(gauge.classification, 0) + 1
            confidence_scores.append(gauge.confidence_score)
        
        return {
            'classification_counts': classifications,
            'confidence_stats': {
                'mean': np.mean(confidence_scores),
                'median': np.median(confidence_scores),
                'std': np.std(confidence_scores),
                'min': np.min(confidence_scores),
                'max': np.max(confidence_scores)
            }
        }
    
    def _analyze_models(self, gauges: List[EnhancedGauge]) -> Dict:
        """Analyze gauge models"""
        model_stats = {
            'total_with_models': sum(1 for g in gauges if g.gauge_model),
            'quality_verified_models': sum(1 for g in gauges if g.gauge_model and g.gauge_model.quality_verified),
            'units_distribution': {},
            'threshold_analysis': {}
        }
        
        # Analyze units
        for gauge in gauges:
            if gauge.gauge_model:
                unit = gauge.gauge_model.gauge_value_unit.value
                model_stats['units_distribution'][unit] = model_stats['units_distribution'].get(unit, 0) + 1
        
        # Analyze thresholds
        warning_levels = []
        danger_levels = []
        extreme_levels = []
        
        for gauge in gauges:
            if gauge.gauge_model:
                thresholds = gauge.gauge_model.thresholds
                warning_levels.append(thresholds.warning_level)
                danger_levels.append(thresholds.danger_level)
                if thresholds.extreme_danger_level:
                    extreme_levels.append(thresholds.extreme_danger_level)
        
        if warning_levels:
            model_stats['threshold_analysis'] = {
                'warning_level_stats': {
                    'mean': np.mean(warning_levels),
                    'min': np.min(warning_levels),
                    'max': np.max(warning_levels)
                },
                'danger_level_stats': {
                    'mean': np.mean(danger_levels),
                    'min': np.min(danger_levels),
                    'max': np.max(danger_levels)
                }
            }
            
            if extreme_levels:
                model_stats['threshold_analysis']['extreme_level_stats'] = {
                    'mean': np.mean(extreme_levels),
                    'min': np.min(extreme_levels),
                    'max': np.max(extreme_levels)
                }
        
        return model_stats
    
    def _analyze_flood_status(self, gauges: List[EnhancedGauge]) -> Dict:
        """Analyze current flood status"""
        status_analysis = {
            'total_with_status': sum(1 for g in gauges if g.flood_status),
            'severity_distribution': {},
            'active_floods': 0,
            'trend_analysis': {}
        }
        
        for gauge in gauges:
            if gauge.flood_status:
                severity = gauge.flood_status.severity.value
                status_analysis['severity_distribution'][severity] = status_analysis['severity_distribution'].get(severity, 0) + 1
                
                if gauge.flood_status.is_active_flood:
                    status_analysis['active_floods'] += 1
                
                trend = gauge.flood_status.forecast_trend.value
                status_analysis['trend_analysis'][trend] = status_analysis['trend_analysis'].get(trend, 0) + 1
        
        return status_analysis
    
    def _analyze_reliability(self, gauges: List[EnhancedGauge]) -> Dict:
        """Analyze gauge reliability for alerting"""
        reliability_tiers = {
            'tier_1_highest': [],  # Quality verified, physical, high confidence, with model
            'tier_2_high': [],     # Quality verified, likely physical, with model
            'tier_3_medium': [],   # Quality verified, uncertain/virtual but with model
            'tier_4_low': []       # All others
        }
        
        for gauge in gauges:
            if (gauge.quality_verified and 
                gauge.classification == GaugeClassification.VERIFIED_PHYSICAL and
                gauge.confidence_score >= 80 and
                gauge.gauge_model and gauge.gauge_model.quality_verified):
                reliability_tiers['tier_1_highest'].append(gauge.gauge_id)
            elif (gauge.quality_verified and
                  gauge.classification == GaugeClassification.LIKELY_PHYSICAL and
                  gauge.gauge_model):
                reliability_tiers['tier_2_high'].append(gauge.gauge_id)
            elif gauge.quality_verified and gauge.gauge_model:
                reliability_tiers['tier_3_medium'].append(gauge.gauge_id)
            else:
                reliability_tiers['tier_4_low'].append(gauge.gauge_id)
        
        return {
            'reliability_tiers': {k: len(v) for k, v in reliability_tiers.items()},
            'tier_details': reliability_tiers,
            'recommended_for_alerts': len(reliability_tiers['tier_1_highest']) + len(reliability_tiers['tier_2_high'])
        }
    
    def _rank_gauges_by_priority(self, gauges: List[EnhancedGauge]) -> List[Dict]:
        """Rank gauges by alert priority"""
        priorities = []
        
        for gauge in gauges:
            priority_info = {
                'gauge_id': gauge.gauge_id,
                'site_name': gauge.site_name,
                'river': gauge.river,
                'priority_score': gauge.alert_priority,
                'classification': gauge.classification,
                'confidence_score': gauge.confidence_score,
                'quality_verified': gauge.quality_verified,
                'has_model': gauge.has_model,
                'current_severity': gauge.flood_status.severity.value if gauge.flood_status else 'NO_DATA',
                'is_reliable': gauge.is_reliable
            }
            priorities.append(priority_info)
        
        # Sort by priority score (highest first)
        priorities.sort(key=lambda x: x['priority_score'], reverse=True)
        
        return priorities
    
    def _generate_system_recommendations(self, gauges: List[EnhancedGauge]) -> Dict:
        """Generate system implementation recommendations"""
        reliable_gauges = [g for g in gauges if g.is_reliable]
        active_floods = [g for g in gauges if g.flood_status and g.flood_status.is_active_flood]
        
        recommendations = {
            'immediate_deployment': {
                'gauge_count': len(reliable_gauges),
                'description': f'Deploy Pak-FEWS with {len(reliable_gauges)} reliable gauges',
                'gauge_ids': [g.gauge_id for g in reliable_gauges[:10]]  # Top 10
            },
            'active_monitoring': {
                'flood_count': len(active_floods),
                'description': f'Monitor {len(active_floods)} gauges with active flood conditions',
                'priority_gauges': [g.gauge_id for g in active_floods if g.is_reliable]
            },
            'system_architecture': {
                'alert_tiers': 'Implement 4-tier reliability system',
                'confidence_display': 'Show confidence levels to users',
                'user_feedback': 'Collect feedback to improve classifications'
            },
            'coverage_expansion': {
                'verify_hybas': f'Verify {sum(1 for g in gauges if g.source == "HYBAS" and g.quality_verified)} HYBAS gauges',
                'contact_google': 'Request clarification for uncertain gauges',
                'local_validation': 'Partner with WAPDA/PMD for ground truth'
            }
        }
        
        return recommendations
    
    def _analyze_coverage(self, gauges: List[EnhancedGauge]) -> Dict:
        """Analyze geographic and river coverage"""
        rivers = {}
        provinces = {'Northern': 0, 'Central': 0, 'Southern': 0}
        
        for gauge in gauges:
            # River analysis
            river = gauge.river or 'Unknown'
            if river not in rivers:
                rivers[river] = {'total': 0, 'reliable': 0, 'with_floods': 0}
            rivers[river]['total'] += 1
            if gauge.is_reliable:
                rivers[river]['reliable'] += 1
            if gauge.flood_status and gauge.flood_status.is_active_flood:
                rivers[river]['with_floods'] += 1
            
            # Regional analysis
            lat = gauge.location.get('latitude', 0)
            if lat >= 34:
                provinces['Northern'] += 1
            elif lat >= 28:
                provinces['Central'] += 1
            else:
                provinces['Southern'] += 1
        
        return {
            'river_coverage': rivers,
            'regional_distribution': provinces,
            'major_rivers_covered': len([r for r, stats in rivers.items() if stats['total'] >= 2 and r != 'Unknown'])
        }
    
    def _save_comprehensive_results(self, gauges: List[EnhancedGauge], analysis: Dict) -> Dict:
        """Save all comprehensive analysis results"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        file_paths = {}
        
        # Create comprehensive DataFrame
        df_data = []
        for gauge in gauges:
            row = {
                'gaugeId': gauge.gauge_id,
                'siteName': gauge.site_name,
                'river': gauge.river,
                'latitude': gauge.location.get('latitude', 0),
                'longitude': gauge.location.get('longitude', 0),
                'source': gauge.source,
                'countryCode': gauge.country_code,
                'qualityVerified': gauge.quality_verified,
                'hasModel': gauge.has_model,
                'classification': gauge.classification,
                'confidenceScore': gauge.confidence_score,
                'isReliable': gauge.is_reliable,
                'alertPriority': gauge.alert_priority,
                'externalMatches': gauge.external_validation.get('matches', []),
                'evidence': '; '.join(gauge.evidence)
            }
            
            # Add model data
            if gauge.gauge_model:
                row.update({
                    'modelId': gauge.gauge_model.gauge_model_id,
                    'modelQualityVerified': gauge.gauge_model.quality_verified,
                    'valueUnit': gauge.gauge_model.gauge_value_unit.value,
                    'warningLevel': gauge.gauge_model.thresholds.warning_level,
                    'dangerLevel': gauge.gauge_model.thresholds.danger_level,
                    'extremeDangerLevel': gauge.gauge_model.thresholds.extreme_danger_level
                })
            
            # Add flood status data
            if gauge.flood_status:
                row.update({
                    'currentSeverity': gauge.flood_status.severity.value,
                    'forecastTrend': gauge.flood_status.forecast_trend.value,
                    'isActiveFlood': gauge.flood_status.is_active_flood,
                    'hasInundationMaps': gauge.flood_status.has_inundation_maps,
                    'floodStatusIssued': gauge.flood_status.issued_time
                })
            
            df_data.append(row)
        
        # Save comprehensive dataset
        df = pd.DataFrame(df_data)
        csv_filename = f'comprehensive_flood_analysis_{timestamp}.csv'
        df.to_csv(csv_filename, index=False)
        file_paths['comprehensive_data'] = csv_filename
        
        # Save analysis report
        analysis_filename = f'comprehensive_analysis_report_{timestamp}.json'
        with open(analysis_filename, 'w') as f:
            json.dump(analysis, f, indent=2, default=str)
        file_paths['analysis_report'] = analysis_filename
        
        # Save priority ranking
        priority_filename = f'gauge_priority_ranking_{timestamp}.csv'
        priority_df = pd.DataFrame(analysis['priority_ranking'])
        priority_df.to_csv(priority_filename, index=False)
        file_paths['priority_ranking'] = priority_filename
        
        # Save executive summary
        summary_filename = f'executive_summary_{timestamp}.md'
        self._generate_executive_summary(analysis, summary_filename)
        file_paths['executive_summary'] = summary_filename
        
        return file_paths
    
    def _generate_executive_summary(self, analysis: Dict, filename: str):
        """Generate executive summary markdown"""
        summary = analysis['summary']
        reliability = analysis['reliability_analysis']
        flood_status = analysis['flood_status_analysis']
        
        content = f"""# Pakistan Comprehensive Flood Analysis - Executive Summary

## Analysis Overview
- **Analysis Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Total Gauges Analyzed**: {summary['total_gauges']}
- **Data Sources**: Google Flood Hub (gauges, gaugeModels, floodStatus APIs)

## Key Findings

### System Readiness
- **Reliable Gauges for Alerts**: {summary['reliable_gauges']} ({(summary['reliable_gauges']/summary['total_gauges']*100):.1f}%)
- **Quality Verified**: {summary['quality_verified']} ({(summary['quality_verified']/summary['total_gauges']*100):.1f}%)
- **With Flood Models**: {summary['with_models']} ({(summary['with_models']/summary['total_gauges']*100):.1f}%)

### Current Flood Situation
- **Active Flood Alerts**: {summary['active_floods']}
- **Gauges with Status Data**: {summary['with_flood_status']}
- **Severity Distribution**: {dict(flood_status['severity_distribution'])}

### Reliability Assessment
The analysis categorizes gauges into 4 reliability tiers:

1. **Tier 1 (Highest)**: {reliability['reliability_tiers']['tier_1_highest']} gauges
   - Quality verified, physically confirmed, high confidence, with verified models
   - **Recommended for immediate deployment**

2. **Tier 2 (High)**: {reliability['reliability_tiers']['tier_2_high']} gauges  
   - Quality verified, likely physical, with models
   - **Suitable for standard alerts**

3. **Tier 3 (Medium)**: {reliability['reliability_tiers']['tier_3_medium']} gauges
   - Quality verified with models but uncertain classification
   - **Use with caution flags**

4. **Tier 4 (Low)**: {reliability['reliability_tiers']['tier_4_low']} gauges
   - Limited verification or missing models
   - **Avoid for critical alerts**

## Implementation Recommendations

### Phase 1: Immediate Deployment
- Deploy Pak-FEWS with **{reliability['recommended_for_alerts']} reliable gauges** (Tiers 1 & 2)
- Focus on gauges with active flood monitoring capabilities
- Implement confidence-based alert reliability indicators

### Phase 2: Enhanced Coverage  
- Verify additional HYBAS gauges through local validation
- Request Google clarification for uncertain classifications
- Expand inundation mapping coverage

### Phase 3: System Enhancement
- Implement user feedback system for classification improvement
- Add real-time threshold monitoring
- Integrate with existing NDMA/PDMA systems

## Risk Assessment
- **{summary['active_floods']} gauges currently showing flood conditions**
- **{reliability['recommended_for_alerts']} gauges ready for reliable alerting**
- System provides **{(reliability['recommended_for_alerts']/summary['total_gauges']*100):.1f}% coverage** with high-confidence alerts

## Next Steps
1. **Technical Implementation**: Begin with Tier 1 & 2 gauges
2. **Stakeholder Engagement**: Present findings to NDMA/PDMA
3. **System Integration**: Connect with existing warning systems
4. **Continuous Improvement**: Implement feedback loops for accuracy enhancement

---
*Analysis powered by comprehensive integration of Google Flood Hub APIs*
*For technical details, see comprehensive analysis report*
"""
        
        with open(filename, 'w') as f:
            f.write(content)

def main():
    """Run comprehensive analysis"""
    analyzer = ComprehensiveFloodAnalyzer()
    results = analyzer.run_comprehensive_analysis()
    
    # Print summary
    analysis = results['analysis']
    summary = analysis['summary']
    
    print("\n" + "="*70)
    print("COMPREHENSIVE PAKISTAN FLOOD HUB ANALYSIS")
    print("="*70)
    
    print(f"\n📊 SUMMARY STATISTICS")
    print(f"Total Gauges: {summary['total_gauges']}")
    print(f"Quality Verified: {summary['quality_verified']} ({(summary['quality_verified']/summary['total_gauges']*100):.1f}%)")
    print(f"Reliable for Alerts: {summary['reliable_gauges']} ({(summary['reliable_gauges']/summary['total_gauges']*100):.1f}%)")
    print(f"Active Floods: {summary['active_floods']}")
    
    print(f"\n🎯 RELIABILITY TIERS")
    reliability = analysis['reliability_analysis']
    for tier, count in reliability['reliability_tiers'].items():
        tier_name = tier.replace('_', ' ').title()
        print(f"{tier_name}: {count} gauges")
    
    print(f"\n🚨 TOP PRIORITY GAUGES")
    for i, gauge in enumerate(analysis['priority_ranking'][:5], 1):
        print(f"{i}. {gauge['gauge_id']} - {gauge['site_name']} (Priority: {gauge['priority_score']})")
    
    print(f"\n📁 FILES GENERATED")
    for file_type, filepath in results['file_paths'].items():
        print(f"{file_type}: {filepath}")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    main()