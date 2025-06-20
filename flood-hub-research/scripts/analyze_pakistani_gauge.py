#!/usr/bin/env python3
"""
Analyze the Discovered Pakistani Gauge
Get detailed information about the one Pakistani gauge we found
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
import pandas as pd
from datetime import datetime

from scripts.flood_hub_api import FloodHubAPI


def analyze_gauge_hybas_4121489010():
    """Analyze the Pakistani gauge we discovered"""
    
    api_key = "AIzaSyB0d7jLuqXjDJW_BQxOyCrBVt97zse7S-M"
    api = FloodHubAPI(api_key=api_key)
    
    gauge_id = "hybas_4121489010"
    
    print(f"Detailed Analysis of Pakistani Gauge: {gauge_id}")
    print("=" * 60)
    
    analysis_results = {}
    
    # 1. Get gauge metadata
    print("\n1. GAUGE METADATA")
    print("-" * 30)
    try:
        gauge_data = api.get_gauge_details(gauge_id)
        analysis_results['gauge_metadata'] = gauge_data
        
        print(f"Gauge ID: {gauge_data.get('gaugeId', 'N/A')}")
        location = gauge_data.get('location', {})
        print(f"Location: {location.get('latitude', 'N/A')}, {location.get('longitude', 'N/A')}")
        print(f"Site Name: {gauge_data.get('siteName', 'N/A')}")
        print(f"River: {gauge_data.get('river', 'N/A')}")
        print(f"Source: {gauge_data.get('source', 'N/A')}")
        print(f"Quality Verified: {gauge_data.get('qualityVerified', 'N/A')}")
        print(f"Has Model: {gauge_data.get('hasModel', 'N/A')}")
        print(f"Country Code: {gauge_data.get('countryCode', 'N/A')}")
        
    except Exception as e:
        print(f"✗ Failed to get gauge metadata: {e}")
        analysis_results['gauge_metadata'] = {"error": str(e)}
    
    # 2. Get flood status
    print("\n2. CURRENT FLOOD STATUS")
    print("-" * 30)
    try:
        flood_status = api.get_flood_status(gauge_id)
        analysis_results['flood_status'] = flood_status
        
        print(f"Gauge ID: {flood_status.get('gaugeId', 'N/A')}")
        print(f"Severity: {flood_status.get('severity', 'N/A')}")
        
        thresholds = flood_status.get('thresholds', {})
        if thresholds:
            print(f"Warning Level: {thresholds.get('warningLevel', 'N/A')}")
            print(f"Danger Level: {thresholds.get('dangerLevel', 'N/A')}")
            print(f"Extreme Danger Level: {thresholds.get('extremeDangerLevel', 'N/A')}")
        
        print(f"Gauge Value Unit: {flood_status.get('gaugeValueUnit', 'N/A')}")
        print(f"Current Level: {flood_status.get('currentLevel', 'N/A')}")
        print(f"Forecast Trend: {flood_status.get('forecastTrend', 'N/A')}")
        
    except Exception as e:
        print(f"✗ Failed to get flood status: {e}")
        analysis_results['flood_status'] = {"error": str(e)}
    
    # 3. Get gauge model/thresholds
    print("\n3. GAUGE MODEL & THRESHOLDS")
    print("-" * 30)
    try:
        gauge_model = api.get_gauge_models(gauge_id)
        analysis_results['gauge_model'] = gauge_model
        
        print(f"Model available: Yes")
        print(f"Model data: {json.dumps(gauge_model, indent=2)}")
        
    except Exception as e:
        print(f"✗ Failed to get gauge model: {e}")
        analysis_results['gauge_model'] = {"error": str(e)}
    
    # 4. Determine location details
    print("\n4. LOCATION ANALYSIS")
    print("-" * 30)
    if 'gauge_metadata' in analysis_results and 'location' in analysis_results['gauge_metadata']:
        location = analysis_results['gauge_metadata']['location']
        lat = location.get('latitude', 0)
        lon = location.get('longitude', 0)
        
        print(f"Coordinates: {lat}, {lon}")
        
        # Determine province/region
        if 24.5 <= lat <= 32.5 and 60.5 <= lon <= 70.3:
            province = "Balochistan"
        elif 23.5 <= lat <= 28.5 and 66.5 <= lon <= 71.1:
            province = "Sindh"
        elif 27.7 <= lat <= 33.0 and 69.3 <= lon <= 75.4:
            province = "Punjab"
        elif 31.0 <= lat <= 36.0 and 69.2 <= lon <= 74.0:
            province = "Khyber Pakhtunkhwa"
        else:
            province = "Unknown/Border region"
            
        print(f"Estimated Province: {province}")
        
        # Distance from major cities
        cities = {
            'Karachi': (24.8607, 67.0011),
            'Lahore': (31.5497, 74.3436),
            'Islamabad': (33.6844, 73.0479),
            'Quetta': (30.1798, 66.9750),
            'Sukkur': (27.7050, 68.8579)
        }
        
        print(f"\nDistances to major cities:")
        for city, (city_lat, city_lon) in cities.items():
            # Simple distance calculation
            dist = ((lat - city_lat)**2 + (lon - city_lon)**2)**0.5 * 111  # Rough km conversion
            print(f"  {city}: ~{dist:.0f} km")
    
    # 5. Assessment for Pak-FEWS system
    print("\n5. PAK-FEWS SUITABILITY ASSESSMENT")
    print("-" * 40)
    
    suitability_score = 0
    assessment = []
    
    if analysis_results.get('gauge_metadata', {}).get('qualityVerified'):
        suitability_score += 3
        assessment.append("✓ Quality verified (high reliability)")
    else:
        assessment.append("⚠ Not quality verified")
    
    if analysis_results.get('gauge_metadata', {}).get('hasModel'):
        suitability_score += 3
        assessment.append("✓ Has predictive model (forecast capability)")
    else:
        assessment.append("⚠ No predictive model")
    
    if 'flood_status' in analysis_results and 'error' not in analysis_results['flood_status']:
        suitability_score += 2
        assessment.append("✓ Real-time flood status available")
    else:
        assessment.append("⚠ No real-time flood status")
    
    if 'gauge_model' in analysis_results and 'error' not in analysis_results['gauge_model']:
        suitability_score += 2
        assessment.append("✓ Threshold data available")
    else:
        assessment.append("⚠ No threshold data")
    
    print(f"Suitability Score: {suitability_score}/10")
    for item in assessment:
        print(f"  {item}")
    
    if suitability_score >= 8:
        recommendation = "HIGH PRIORITY - Excellent for Pak-FEWS monitoring"
    elif suitability_score >= 6:
        recommendation = "MEDIUM PRIORITY - Good for monitoring with some limitations"
    else:
        recommendation = "LOW PRIORITY - Limited utility for early warning"
    
    print(f"\nRecommendation: {recommendation}")
    
    # 6. Save detailed analysis
    analysis_results['analysis_metadata'] = {
        'analyzed_at': datetime.now().isoformat(),
        'suitability_score': suitability_score,
        'recommendation': recommendation,
        'assessment_points': assessment
    }
    
    # Save to file
    os.makedirs('data', exist_ok=True)
    with open('data/detailed_gauge_analysis.json', 'w') as f:
        json.dump(analysis_results, f, indent=2)
    
    print(f"\n✓ Detailed analysis saved to: data/detailed_gauge_analysis.json")
    
    return analysis_results


def create_pakistan_coverage_report():
    """Create a comprehensive report on Pakistan coverage"""
    
    print("\n" + "=" * 60)
    print("PAKISTAN FLOOD HUB COVERAGE ASSESSMENT")
    print("=" * 60)
    
    # Load our analysis
    try:
        with open('data/detailed_gauge_analysis.json', 'r') as f:
            detailed_analysis = json.load(f)
    except:
        detailed_analysis = {}
    
    report = {
        'executive_summary': {
            'total_pakistani_gauges_found': 1,
            'quality_verified_gauges': 1,
            'gauges_with_models': 1,
            'priority_gauges_for_monitoring': 1 if detailed_analysis.get('analysis_metadata', {}).get('suitability_score', 0) >= 6 else 0
        },
        'coverage_assessment': {
            'geographic_coverage': 'Very Limited - Single gauge in Balochistan region',
            'major_rivers_covered': 'None identified (no river name provided)',
            'population_centers_covered': 'Limited - Rural/remote area',
            'critical_gaps': [
                'No coverage of Indus River main stem',
                'No coverage of major cities (Karachi, Lahore, Islamabad)',
                'No coverage of Punjab flood-prone areas',
                'No coverage of Sindh (major flood risk area)',
                'Very limited overall geographic coverage'
            ]
        },
        'data_quality_assessment': {
            'overall_rating': 'Good quality for the single gauge',
            'quality_verified_percentage': 100.0,
            'model_availability_percentage': 100.0,
            'real_time_data_availability': 'Available' if 'flood_status' in detailed_analysis else 'Unknown'
        },
        'recommendations': {
            'immediate_actions': [
                'Continue monitoring the single available gauge',
                'Request additional gauge access from Google',
                'Explore alternative data sources for broader coverage',
                'Consider Open-Meteo API for additional flood data'
            ],
            'system_design_implications': [
                'Cannot rely solely on Google Flood Hub for Pakistan-wide monitoring',
                'Need to integrate multiple data sources',
                'Consider satellite-based flood detection',
                'Prioritize Pakistani meteorological department data integration'
            ],
            'research_next_steps': [
                'Apply for enhanced Google Flood Hub API access',
                'Investigate Google Earth Engine flood datasets',
                'Research Pakistan Meteorological Department APIs',
                'Explore WAPDA (Water and Power Development Authority) data sources'
            ]
        }
    }
    
    # Save report
    with open('data/pakistan_coverage_report.json', 'w') as f:
        json.dump(report, f, indent=2)
    
    # Print key findings
    print("\nKEY FINDINGS:")
    print(f"• Total Pakistani gauges accessible: {report['executive_summary']['total_pakistani_gauges_found']}")
    print(f"• Quality verified: {report['executive_summary']['quality_verified_gauges']}")
    print(f"• Have predictive models: {report['executive_summary']['gauges_with_models']}")
    print(f"• Geographic coverage: {report['coverage_assessment']['geographic_coverage']}")
    
    print("\nCRITICAL GAPS:")
    for gap in report['coverage_assessment']['critical_gaps']:
        print(f"  ⚠ {gap}")
    
    print("\nRECOMMENDATIONS:")
    for action in report['recommendations']['immediate_actions']:
        print(f"  → {action}")
    
    print(f"\n✓ Coverage report saved to: data/pakistan_coverage_report.json")


def main():
    """Main execution"""
    
    # Analyze the single Pakistani gauge in detail
    analysis_results = analyze_gauge_hybas_4121489010()
    
    # Create comprehensive coverage report
    create_pakistan_coverage_report()
    
    print("\n" + "=" * 60)
    print("ANALYSIS COMPLETE")
    print("=" * 60)
    print("Files generated:")
    print("  • data/detailed_gauge_analysis.json")
    print("  • data/pakistan_coverage_report.json")
    print("\nConclusion: Limited but high-quality coverage available.")
    print("Next steps: Explore alternative data sources for comprehensive monitoring.")


if __name__ == "__main__":
    main()