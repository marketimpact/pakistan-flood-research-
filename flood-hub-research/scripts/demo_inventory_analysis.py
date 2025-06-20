#!/usr/bin/env python3
"""
Demo Gauge Inventory Analysis
Analyzes mock Pakistani gauge data to demonstrate research approach
"""

import json
import pandas as pd
from datetime import datetime
import os
from typing import List, Dict


def load_sample_data() -> List[Dict]:
    """Load sample gauge data"""
    with open('data/sample_gauge_inventory.json', 'r') as f:
        return json.load(f)


def determine_province(gauge_id: str) -> str:
    """Extract province from gauge ID"""
    province_mapping = {
        'punjab': 'Punjab',
        'sindh': 'Sindh', 
        'khyber_pakhtunkhwa': 'Khyber Pakhtunkhwa',
        'balochistan': 'Balochistan',
        'gilgit_baltistan': 'Gilgit-Baltistan'
    }
    
    for key, province in province_mapping.items():
        if key in gauge_id.lower():
            return province
    return 'Unknown'


def create_gauge_dataframe(gauges: List[Dict]) -> pd.DataFrame:
    """Convert gauge list to pandas DataFrame"""
    rows = []
    
    for gauge in gauges:
        row = {
            'gaugeId': gauge.get('gaugeId', ''),
            'latitude': gauge.get('location', {}).get('latitude', None),
            'longitude': gauge.get('location', {}).get('longitude', None),
            'river': gauge.get('river', ''),
            'siteName': gauge.get('siteName', ''),
            'qualityVerified': gauge.get('qualityVerified', False),
            'hasModel': gauge.get('hasModel', False),
            'source': gauge.get('source', ''),
            'countryCode': gauge.get('countryCode', ''),
            'province': determine_province(gauge['gaugeId']),
            'query_timestamp': datetime.now().isoformat()
        }
        rows.append(row)
    
    return pd.DataFrame(rows)


def analyze_inventory(df: pd.DataFrame) -> Dict:
    """Generate comprehensive analysis of gauge inventory"""
    analysis = {
        'total_gauges': len(df),
        'quality_verified': len(df[df['qualityVerified'] == True]),
        'has_model': len(df[df['hasModel'] == True]),
        'quality_and_model': len(df[(df['qualityVerified'] == True) & (df['hasModel'] == True)]),
        'by_province': df['province'].value_counts().to_dict(),
        'by_source': df['source'].value_counts().to_dict(),
        'rivers_with_names': len(df[df['river'] != '']),
        'sites_with_names': len(df[df['siteName'] != '']),
        'unique_rivers': df[df['river'] != '']['river'].nunique(),
        'river_list': df[df['river'] != '']['river'].unique().tolist()
    }
    
    # Calculate percentages
    if analysis['total_gauges'] > 0:
        analysis['quality_verified_pct'] = round(100 * analysis['quality_verified'] / analysis['total_gauges'], 1)
        analysis['has_model_pct'] = round(100 * analysis['has_model'] / analysis['total_gauges'], 1)
        analysis['quality_and_model_pct'] = round(100 * analysis['quality_and_model'] / analysis['total_gauges'], 1)
    
    return analysis


def analyze_coverage_by_river(df: pd.DataFrame) -> Dict:
    """Analyze coverage of major Pakistani rivers"""
    major_rivers = ['Indus', 'Jhelum', 'Chenab', 'Ravi', 'Sutlej']
    
    river_analysis = {}
    for river in major_rivers:
        river_gauges = df[df['river'] == river]
        river_analysis[river] = {
            'total_gauges': len(river_gauges),
            'quality_verified': len(river_gauges[river_gauges['qualityVerified'] == True]),
            'has_model': len(river_gauges[river_gauges['hasModel'] == True]),
            'provinces': river_gauges['province'].value_counts().to_dict()
        }
    
    return river_analysis


def generate_research_insights(analysis: Dict, river_analysis: Dict) -> List[str]:
    """Generate key research insights"""
    insights = []
    
    # Data quality insights
    if analysis['quality_verified_pct'] < 50:
        insights.append(f"⚠️  Only {analysis['quality_verified_pct']}% of gauges are quality verified - may limit reliable monitoring")
    else:
        insights.append(f"✓ {analysis['quality_verified_pct']}% of gauges are quality verified - good data quality")
    
    # Model coverage insights
    if analysis['has_model_pct'] > 70:
        insights.append(f"✓ {analysis['has_model_pct']}% of gauges have predictive models - excellent forecast capability")
    elif analysis['has_model_pct'] > 50:
        insights.append(f"✓ {analysis['has_model_pct']}% of gauges have predictive models - good forecast capability")
    else:
        insights.append(f"⚠️  Only {analysis['has_model_pct']}% of gauges have predictive models - limited forecast capability")
    
    # Province coverage insights
    province_counts = analysis['by_province']
    max_province = max(province_counts, key=province_counts.get)
    min_province = min(province_counts, key=province_counts.get)
    insights.append(f"📍 Highest coverage: {max_province} ({province_counts[max_province]} gauges)")
    insights.append(f"📍 Lowest coverage: {min_province} ({province_counts[min_province]} gauges)")
    
    # River coverage insights
    indus_coverage = river_analysis.get('Indus', {}).get('total_gauges', 0)
    if indus_coverage > 0:
        insights.append(f"🌊 Indus River: {indus_coverage} gauges (Pakistan's main river)")
    
    # Critical gaps
    if analysis['quality_and_model'] < analysis['total_gauges'] * 0.4:
        insights.append("⚠️  Less than 40% of gauges have both quality verification AND models - significant monitoring gaps")
    
    return insights


def main():
    """Main analysis execution"""
    print("Pakistan Flood Hub Demo Analysis")
    print("=" * 50)
    print("Note: Using mock data to demonstrate research approach")
    print("=" * 50)
    
    # Load sample data
    print("\n1. Loading sample gauge data...")
    gauges = load_sample_data()
    print(f"   Loaded {len(gauges)} sample gauges")
    
    # Create DataFrame
    print("\n2. Processing gauge data...")
    df = create_gauge_dataframe(gauges)
    
    # Save processed data
    output_path = 'data/processed_gauge_inventory.csv'
    df.to_csv(output_path, index=False)
    print(f"   Saved processed data to: {output_path}")
    
    # Analyze data
    print("\n3. Analyzing gauge inventory...")
    analysis = analyze_inventory(df)
    river_analysis = analyze_coverage_by_river(df)
    
    # Save analysis
    full_analysis = {
        'summary': analysis,
        'river_coverage': river_analysis,
        'generated_at': datetime.now().isoformat()
    }
    
    analysis_path = 'data/demo_coverage_analysis.json'
    with open(analysis_path, 'w') as f:
        json.dump(full_analysis, f, indent=2)
    print(f"   Saved analysis to: {analysis_path}")
    
    # Generate insights
    insights = generate_research_insights(analysis, river_analysis)
    
    # Print comprehensive results
    print("\n" + "=" * 60)
    print("COMPREHENSIVE ANALYSIS RESULTS")
    print("=" * 60)
    
    print(f"\n📊 OVERALL STATISTICS")
    print(f"Total gauges: {analysis['total_gauges']}")
    print(f"Quality verified: {analysis['quality_verified']} ({analysis.get('quality_verified_pct', 0)}%)")
    print(f"Has model: {analysis['has_model']} ({analysis.get('has_model_pct', 0)}%)")
    print(f"Both quality verified AND has model: {analysis['quality_and_model']} ({analysis.get('quality_and_model_pct', 0)}%)")
    
    print(f"\n📍 COVERAGE BY PROVINCE")
    for province, count in sorted(analysis['by_province'].items(), key=lambda x: x[1], reverse=True):
        print(f"  {province}: {count} gauges")
    
    print(f"\n🏢 DATA SOURCES")
    for source, count in sorted(analysis['by_source'].items(), key=lambda x: x[1], reverse=True):
        print(f"  {source}: {count} gauges")
    
    print(f"\n🌊 MAJOR RIVERS COVERAGE")
    for river, data in river_analysis.items():
        print(f"  {river}: {data['total_gauges']} gauges ({data['quality_verified']} quality verified)")
    
    print(f"\n💡 KEY RESEARCH INSIGHTS")
    for i, insight in enumerate(insights, 1):
        print(f"  {i}. {insight}")
    
    print(f"\n📈 DATA COMPLETENESS")
    print(f"Rivers with names: {analysis['rivers_with_names']}/{analysis['total_gauges']} ({100*analysis['rivers_with_names']//analysis['total_gauges']}%)")
    print(f"Sites with names: {analysis['sites_with_names']}/{analysis['total_gauges']} ({100*analysis['sites_with_names']//analysis['total_gauges']}%)")
    print(f"Unique rivers monitored: {analysis['unique_rivers']}")
    
    print(f"\n🎯 PRIORITY GAUGES FOR PAK-FEWS")
    priority_gauges = df[(df['qualityVerified'] == True) & (df['hasModel'] == True)]
    print(f"Recommended for monitoring: {len(priority_gauges)} gauges")
    
    if len(priority_gauges) > 0:
        print("\nTop 10 priority gauges by major rivers:")
        priority_sample = priority_gauges[priority_gauges['river'].isin(['Indus', 'Jhelum', 'Chenab', 'Ravi', 'Sutlej'])].head(10)
        for _, gauge in priority_sample.iterrows():
            print(f"  • {gauge['gaugeId']} - {gauge['river']} at {gauge['siteName']} ({gauge['province']})")
    
    print(f"\n" + "=" * 60)
    print("FILES GENERATED:")
    print("• data/processed_gauge_inventory.csv - Complete gauge inventory")
    print("• data/demo_coverage_analysis.json - Detailed analysis results")
    print("=" * 60)


if __name__ == "__main__":
    main()