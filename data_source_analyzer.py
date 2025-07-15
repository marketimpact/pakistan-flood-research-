#!/usr/bin/env python3
"""
Comprehensive Data Source Analyzer for Google Flood Hub
Implements the three-layer query approach to understand gauge data sources
"""

import requests
import json
import time
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
from config import config

logger = logging.getLogger(__name__)

class FloodHubAPIClient:
    """Rate-limited API client for Google Flood Hub"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://floodforecasting.googleapis.com/v1"
        self.last_request = datetime.now()
        self.min_delay = 0.5  # seconds between requests
        
        self.data_source_indicators = {
            # From /gauges endpoint
            "source": {
                "HYBAS": "HydroBASINS (likely virtual)",
                "GRDC": "Global Runoff Data Center (physical)",
                "WAPDA": "Pakistan Water Authority (physical)",
                "PMD": "Pakistan Meteorological Department (physical)",
                "CARAVAN": "Caravan dataset gauge"
            },
            
            # From /gaugeModels endpoint  
            "gaugeValueUnit": {
                "CUBIC_METERS_PER_SECOND": "Discharge model (often virtual)",
                "METERS": "Water level (often physical)"
            },
            
            # From /floodStatus endpoint
            "mapInferenceType": {
                "MODEL": "AI-based prediction",
                "IMAGE_CLASSIFICATION": "Satellite imagery validation"
            },
            
            "inundationMapType": {
                "PROBABILITY": "Statistical model output",
                "DEPTH": "Physics-based calculation"
            }
        }
    
    def rate_limited_request(self, url: str, method: str = "GET", params: dict = None, json_data: dict = None) -> requests.Response:
        """Make API request with rate limiting"""
        
        # Enforce rate limit
        elapsed = (datetime.now() - self.last_request).total_seconds()
        if elapsed < self.min_delay:
            time.sleep(self.min_delay - elapsed)
        
        headers = {
            "Content-Type": "application/json"
        }
        
        if params is None:
            params = {}
        
        if self.api_key:
            params["key"] = self.api_key
        
        try:
            if method.upper() == "POST":
                response = requests.post(url, headers=headers, params=params, json=json_data, timeout=30)
            else:
                response = requests.get(url, headers=headers, params=params, timeout=30)
            
            self.last_request = datetime.now()
            
            if response.status_code == 429:  # Rate limited
                retry_after = int(response.headers.get('Retry-After', 60))
                logger.warning(f"Rate limited. Waiting {retry_after} seconds...")
                time.sleep(retry_after)
                return self.rate_limited_request(url, method, params, json_data)  # Retry
            
            return response
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise
    
    def get_gauge_details(self, gauge_id: str) -> Optional[Dict]:
        """Get basic gauge information revealing primary source"""
        
        # Use batchGet to get individual gauge details
        url = f"{self.base_url}/gauges:batchGet"
        params = {"gaugeIds": [gauge_id]}
        
        try:
            response = self.rate_limited_request(url, "GET", params)
            
            if response.status_code == 200:
                data = response.json()
                gauges = data.get("gauges", [])
                
                if gauges:
                    gauge_data = gauges[0]
                    
                    # Extract key source indicators
                    source_info = {
                        "gaugeId": gauge_data.get("gaugeId"),
                        "source": gauge_data.get("source"),
                        "qualityVerified": gauge_data.get("qualityVerified"),
                        "hasModel": gauge_data.get("hasModel"),
                        "siteName": gauge_data.get("siteName", ""),
                        "river": gauge_data.get("river", ""),
                        "location": gauge_data.get("location"),
                        "countryCode": gauge_data.get("countryCode")
                    }
                    
                    # Determine if physical or virtual
                    source_info["likely_physical"] = bool(
                        source_info["siteName"] or 
                        source_info["river"] or
                        source_info["source"] in ["GRDC", "WAPDA", "PMD"]
                    )
                    
                    return source_info
                    
        except Exception as e:
            logger.error(f"Error getting gauge details for {gauge_id}: {e}")
        
        return None
    
    def get_gauge_model(self, gauge_id: str) -> Optional[Dict]:
        """Get model details revealing computation methods"""
        
        url = f"{self.base_url}/gaugeModels:batchGet"
        params = {"names": [f"gaugeModels/{gauge_id}"]}
        
        try:
            response = self.rate_limited_request(url, "GET", params)
            
            if response.status_code == 200:
                data = response.json()
                models = data.get("gaugeModels", [])
                
                if models:
                    model_data = models[0]
                    
                    model_info = {
                        "gaugeModelId": model_data.get("gaugeModelId"),
                        "thresholds": model_data.get("thresholds"),
                        "gaugeValueUnit": model_data.get("gaugeValueUnit"),
                        "qualityVerified": model_data.get("qualityVerified")
                    }
                    
                    # Analyze model characteristics
                    unit = model_info.get("gaugeValueUnit", "")
                    if unit == "CUBIC_METERS_PER_SECOND":
                        model_info["thresholdSource"] = "2/5/20-year return periods"
                        model_info["modelType"] = "discharge_prediction"
                    elif unit == "METERS":
                        model_info["thresholdSource"] = "Local authority thresholds"
                        model_info["modelType"] = "water_level"
                    else:
                        model_info["thresholdSource"] = "Unknown"
                        model_info["modelType"] = "unknown"
                    
                    # Analyze model complexity (hash length as proxy)
                    model_hash = model_info.get("gaugeModelId", "")
                    if model_hash:
                        model_info["modelComplexity"] = len(model_hash)
                        model_info["modelHash"] = model_hash[:10] + "..." if len(model_hash) > 10 else model_hash
                    
                    return model_info
                    
        except Exception as e:
            logger.error(f"Error getting gauge model for {gauge_id}: {e}")
        
        return None
    
    def get_flood_status(self, gauge_id: str) -> Optional[Dict]:
        """Get current predictions revealing data sources"""
        
        url = f"{self.base_url}/floodStatus:queryLatestFloodStatusByGaugeIds"
        json_data = {"gaugeIds": [gauge_id]}
        
        try:
            response = self.rate_limited_request(url, "POST", json_data=json_data)
            
            if response.status_code == 200:
                data = response.json()
                statuses = data.get("floodStatuses", [])
                
                if statuses:
                    status = statuses[0]
                    
                    inference_info = {
                        "mapInferenceType": status.get("mapInferenceType"),
                        "severity": status.get("severity"),
                        "forecastTrend": status.get("forecastTrend"),
                        "hasInundationMap": bool(status.get("inundationMapSet")),
                        "inundationMapType": None,
                        "confidenceLevels": [],
                        "issuedTime": status.get("issuedTime"),
                        "qualityVerified": status.get("qualityVerified")
                    }
                    
                    # Extract inundation data sources
                    if status.get("inundationMapSet"):
                        map_set = status["inundationMapSet"]
                        inference_info["inundationMapType"] = map_set.get("inundationMapType")
                        
                        # Count confidence levels available
                        if "inundationMaps" in map_set:
                            inference_info["confidenceLevels"] = [
                                m.get("level") for m in map_set["inundationMaps"]
                            ]
                    
                    return inference_info
                    
        except Exception as e:
            logger.error(f"Error getting flood status for {gauge_id}: {e}")
        
        return None
    
    def get_complete_gauge_info(self, gauge_id: str) -> Dict:
        """Extract all available data source information for a gauge"""
        
        logger.info(f"Analyzing gauge {gauge_id}...")
        
        gauge_info = {"gaugeId": gauge_id}
        
        # Layer 1: Basic gauge information
        gauge_data = self.get_gauge_details(gauge_id)
        if gauge_data:
            gauge_info.update(gauge_data)
        
        # Layer 2: Model information (if available)
        if gauge_info.get('hasModel'):
            model_data = self.get_gauge_model(gauge_id)
            if model_data:
                gauge_info['model'] = model_data
        
        # Layer 3: Current flood status (reveals inference type)
        flood_status = self.get_flood_status(gauge_id)
        if flood_status:
            gauge_info['status'] = flood_status
        
        # Analyze data sources
        return self.analyze_data_sources(gauge_info)
    
    def analyze_data_sources(self, gauge_info: Dict) -> Dict:
        """Interpret API responses to identify actual data sources"""
        
        analysis = {
            "gaugeId": gauge_info.get("gaugeId"),
            "dataSourceSummary": [],
            "confidence": "unknown",
            "recommendations": [],
            "underlyingDataSources": [],
            "predictionMethods": [],
            "verificationMethods": []
        }
        
        # Analyze primary source
        source = gauge_info.get("source", "")
        
        if source == "HYBAS":
            if gauge_info.get("likely_physical"):
                analysis["dataSourceSummary"].append("HydroBASINS network with possible physical gauge")
                analysis["underlyingDataSources"].extend([
                    "NASA SRTM elevation data (2000)",
                    "Possible physical gauge measurements",
                    "WWF HydroBASINS watershed boundaries"
                ])
            else:
                analysis["dataSourceSummary"].append("Virtual gauge using HydroBASINS watersheds")
                analysis["underlyingDataSources"].extend([
                    "NASA SRTM elevation data (2000)",
                    "WWF HydroBASINS watershed delineation",
                    "IMERG satellite precipitation",
                    "ECMWF ERA5-land reanalysis",
                    "NOAA CPC precipitation data"
                ])
                analysis["predictionMethods"].append("AI LSTM model trained on global data")
        
        elif source == "GRDC":
            analysis["dataSourceSummary"].append("Global Runoff Data Center physical gauge")
            analysis["underlyingDataSources"].extend([
                "Physical streamflow measurements",
                "Historical discharge records",
                "Local gauge infrastructure"
            ])
            analysis["verificationMethods"].append("Direct measurement validation")
        
        elif source in ["WAPDA", "PMD"]:
            analysis["dataSourceSummary"].append(f"Pakistani {source} physical monitoring network")
            analysis["underlyingDataSources"].extend([
                "Pakistani government gauge network",
                "Physical water level/discharge measurements",
                "Local meteorological data"
            ])
            analysis["verificationMethods"].append("Pakistani authority validation")
        
        # Analyze model inference
        model_info = gauge_info.get("model", {})
        if model_info:
            unit = model_info.get("gaugeValueUnit", "")
            if unit == "CUBIC_METERS_PER_SECOND":
                analysis["predictionMethods"].append("Discharge prediction model")
                analysis["underlyingDataSources"].append("Weather forecast data for runoff modeling")
            elif unit == "METERS":
                analysis["predictionMethods"].append("Water level prediction model")
        
        # Analyze flood status inference
        status_info = gauge_info.get("status", {})
        if status_info:
            map_inference = status_info.get("mapInferenceType")
            if map_inference == "MODEL":
                analysis["predictionMethods"].append("Physics-based AI flood extent model")
                analysis["underlyingDataSources"].append("Google DeepMind weather forecasting")
            elif map_inference == "IMAGE_CLASSIFICATION":
                analysis["verificationMethods"].append("Sentinel-1 SAR imagery validation")
                analysis["underlyingDataSources"].append("ESA Sentinel-1 satellite data")
            
            # Analyze inundation mapping
            if status_info.get("hasInundationMap"):
                map_type = status_info.get("inundationMapType")
                if map_type == "PROBABILITY":
                    analysis["predictionMethods"].append("Statistical flood probability mapping")
                elif map_type == "DEPTH":
                    analysis["predictionMethods"].append("Physics-based flood depth modeling")
                    analysis["underlyingDataSources"].append("High-resolution topographic data")
        
        # Determine confidence
        if gauge_info.get("qualityVerified") and gauge_info.get("likely_physical"):
            analysis["confidence"] = "high"
            analysis["recommendations"].extend([
                "Suitable for critical alerts",
                "Validated against physical measurements"
            ])
        elif gauge_info.get("qualityVerified"):
            analysis["confidence"] = "medium"
            analysis["recommendations"].extend([
                "Use with confidence indicators",
                "AI model validated but may be virtual"
            ])
        else:
            analysis["confidence"] = "low"
            analysis["recommendations"].extend([
                "Requires community validation",
                "Use only for supplementary information",
                "Not recommended for emergency alerts"
            ])
        
        return analysis
    
    def generate_gauge_source_report(self, gauge_id: str) -> str:
        """Create human-readable report on gauge data sources"""
        
        info = self.get_complete_gauge_info(gauge_id)
        
        report = f"""
    Data Source Analysis for Gauge: {gauge_id}
    ==========================================
    
    Primary Source: {info.get('source', 'Unknown')}
    Physical Indicators: {'Yes' if info.get('likely_physical') else 'No'}
    Quality Verified: {'Yes' if info.get('qualityVerified') else 'No'}
    Location: {info.get('location', {}).get('latitude', 'N/A')}, {info.get('location', {}).get('longitude', 'N/A')}
    
    Model Information:
    - Has Model: {'Yes' if info.get('hasModel') else 'No'}
    - Measurement Type: {info.get('model', {}).get('gaugeValueUnit', 'Unknown')}
    - Model Type: {info.get('model', {}).get('modelType', 'Unknown')}
    - Threshold Source: {info.get('model', {}).get('thresholdSource', 'Unknown')}
    - Model Hash: {info.get('model', {}).get('modelHash', 'N/A')}
    
    Prediction Method:
    - Map Inference: {info.get('status', {}).get('mapInferenceType', 'None')}
    - Inundation Type: {info.get('status', {}).get('inundationMapType', 'None')}
    - Confidence Levels: {info.get('status', {}).get('confidenceLevels', [])}
    - Current Severity: {info.get('status', {}).get('severity', 'Unknown')}
    
    Underlying Data Sources:
    {chr(10).join(['- ' + s for s in info.get('underlyingDataSources', [])])}
    
    Prediction Methods:
    {chr(10).join(['- ' + s for s in info.get('predictionMethods', [])])}
    
    Verification Methods:
    {chr(10).join(['- ' + s for s in info.get('verificationMethods', [])])}
    
    Data Source Summary:
    {chr(10).join(['- ' + s for s in info.get('dataSourceSummary', [])])}
    
    Confidence Assessment: {info.get('confidence', 'Unknown').upper()}
    
    Recommendations:
    {chr(10).join(['- ' + r for r in info.get('recommendations', [])])}
    """
        
        return report

def analyze_sample_pakistani_gauges():
    """Analyze a sample of Pakistani gauges to understand data source patterns"""
    
    client = FloodHubAPIClient(config.api_key)
    
    # Sample gauge IDs from different regions of Pakistan
    sample_gauges = [
        "hybas_4121440160",  # Quality verified
        "hybas_4121462540",  # Quality verified
        "hybas_4120691110",  # High priority from our analysis
        "hybas_4120791130",  # High priority from our analysis
        "hybas_4121489010",  # From our original test
        "hybas_2120071260",  # From different region
        "hybas_2120071690",  # From different region
        "hybas_2120085550"   # From different region
    ]
    
    results = []
    
    print("🔍 Analyzing Sample Pakistani Gauges for Data Sources...")
    print("="*60)
    
    for i, gauge_id in enumerate(sample_gauges, 1):
        print(f"\n📍 Analyzing gauge {i}/{len(sample_gauges)}: {gauge_id}")
        
        try:
            analysis = client.get_complete_gauge_info(gauge_id)
            results.append(analysis)
            
            # Print key findings
            print(f"   Source: {analysis.get('source', 'Unknown')}")
            print(f"   Quality Verified: {analysis.get('qualityVerified', False)}")
            print(f"   Likely Physical: {analysis.get('likely_physical', False)}")
            print(f"   Confidence: {analysis.get('confidence', 'Unknown')}")
            print(f"   Data Sources: {len(analysis.get('underlyingDataSources', []))}")
            print(f"   Prediction Methods: {len(analysis.get('predictionMethods', []))}")
            
        except Exception as e:
            print(f"   ❌ Error: {e}")
            continue
    
    # Generate summary
    print("\n" + "="*60)
    print("📊 SUMMARY ANALYSIS")
    print("="*60)
    
    if results:
        confidence_dist = {}
        source_dist = {}
        data_source_types = set()
        prediction_methods = set()
        
        for result in results:
            # Count confidence levels
            conf = result.get('confidence', 'unknown')
            confidence_dist[conf] = confidence_dist.get(conf, 0) + 1
            
            # Count sources
            source = result.get('source', 'unknown')
            source_dist[source] = source_dist.get(source, 0) + 1
            
            # Collect data source types
            data_source_types.update(result.get('underlyingDataSources', []))
            prediction_methods.update(result.get('predictionMethods', []))
        
        print(f"Confidence Distribution: {confidence_dist}")
        print(f"Source Distribution: {source_dist}")
        print(f"\nUnique Data Sources Found ({len(data_source_types)}):")
        for ds in sorted(data_source_types):
            print(f"  - {ds}")
        
        print(f"\nPrediction Methods Found ({len(prediction_methods)}):")
        for pm in sorted(prediction_methods):
            print(f"  - {pm}")
    
    return results

def main():
    """Run the data source analysis"""
    
    if not config.api_key:
        print("❌ No API key configured. Please set GOOGLE_FLOOD_HUB_API_KEY")
        return
    
    # Analyze sample gauges
    results = analyze_sample_pakistani_gauges()
    
    # Generate detailed report for first gauge
    if results:
        client = FloodHubAPIClient(config.api_key)
        detailed_report = client.generate_gauge_source_report(results[0]['gaugeId'])
        
        print("\n" + "="*60)
        print("📋 DETAILED REPORT (First Gauge)")
        print("="*60)
        print(detailed_report)
    
    # Save results
    if results:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'data_source_analysis_{timestamp}.json'
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n💾 Detailed results saved to: {filename}")

if __name__ == "__main__":
    main()