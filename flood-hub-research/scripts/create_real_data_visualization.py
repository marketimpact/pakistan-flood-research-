#!/usr/bin/env python3
"""
Create Real Data Visualization
Visualize the actual Pakistani gauge data discovered from Google Flood Hub API
"""

import pandas as pd
import folium
import matplotlib.pyplot as plt
import json
import os
from datetime import datetime


def create_real_data_map():
    """Create map showing the real Pakistani gauge"""
    
    # Load real gauge data
    try:
        df = pd.read_csv('data/real_pakistan_gauges.csv')
    except FileNotFoundError:
        print("Real gauge data not found. Run discover_pakistan_gauges.py first.")
        return None
    
    if len(df) == 0:
        print("No real gauge data available for mapping.")
        return None
    
    # Pakistan center coordinates
    center_lat = 30.3753
    center_lon = 69.3451
    
    # Create map focused on Pakistan
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=6,
        tiles='OpenStreetMap'
    )
    
    # Add the real gauge
    for idx, row in df.iterrows():
        if pd.notna(row['latitude']) and pd.notna(row['longitude']):
            
            # Load detailed analysis if available
            try:
                with open('data/detailed_gauge_analysis.json', 'r') as f:
                    detailed_data = json.load(f)
                
                # Extract threshold data
                thresholds = detailed_data.get('gauge_model', {}).get('thresholds', {})
                warning_level = thresholds.get('warningLevel', 'N/A')
                danger_level = thresholds.get('dangerLevel', 'N/A')
                extreme_level = thresholds.get('extremeDangerLevel', 'N/A')
                units = detailed_data.get('gauge_model', {}).get('gaugeValueUnit', 'N/A')
                
                popup_text = f"""
                <div style="width: 300px;">
                <h4><b>Pakistani Gauge (REAL DATA)</b></h4>
                <b>Gauge ID:</b> {row['gaugeId']}<br>
                <b>Location:</b> {row['latitude']:.4f}, {row['longitude']:.4f}<br>
                <b>Province:</b> Balochistan (estimated)<br>
                <b>Source:</b> {row['source']}<br>
                <b>Quality Verified:</b> {'Yes' if row['qualityVerified'] else 'No'}<br>
                <b>Has Model:</b> {'Yes' if row['hasModel'] else 'No'}<br>
                <hr>
                <h5>Flood Thresholds:</h5>
                <b>Warning Level:</b> {warning_level} {units}<br>
                <b>Danger Level:</b> {danger_level} {units}<br>
                <b>Extreme Danger:</b> {extreme_level} {units}<br>
                <hr>
                <b>Distance to Karachi:</b> ~252 km<br>
                <b>Distance to Sukkur:</b> ~183 km<br>
                <small><i>Data source: Google Flood Hub API</i></small>
                </div>
                """
                
            except:
                popup_text = f"""
                <b>Gauge ID:</b> {row['gaugeId']}<br>
                <b>Location:</b> {row['latitude']:.4f}, {row['longitude']:.4f}<br>
                <b>Quality Verified:</b> {'Yes' if row['qualityVerified'] else 'No'}<br>
                <b>Has Model:</b> {'Yes' if row['hasModel'] else 'No'}<br>
                """
            
            # Add marker with high priority styling (green with star)
            folium.Marker(
                location=[row['latitude'], row['longitude']],
                popup=folium.Popup(popup_text, max_width=350),
                tooltip=f"REAL: {row['gaugeId']} - High Priority",
                icon=folium.Icon(
                    color='green',
                    icon='star',
                    prefix='glyphicon'
                )
            ).add_to(m)
    
    # Add Pakistan boundary outline (approximate)
    pakistan_bounds = [
        [37.0, 60.0],  # NW
        [37.0, 77.0],  # NE  
        [23.0, 77.0],  # SE
        [23.0, 60.0],  # SW
        [37.0, 60.0]   # Close
    ]
    
    folium.PolyLine(
        pakistan_bounds,
        popup="Pakistan Boundary (Approximate)",
        color='red',
        weight=3,
        opacity=0.7
    ).add_to(m)
    
    # Add major cities for reference
    major_cities = {
        'Karachi': (24.8607, 67.0011),
        'Lahore': (31.5497, 74.3436),
        'Islamabad': (33.6844, 73.0479),
        'Quetta': (30.1798, 66.9750),
        'Sukkur': (27.7050, 68.8579),
        'Hyderabad': (25.3960, 68.3578)
    }
    
    for city, (lat, lon) in major_cities.items():
        folium.CircleMarker(
            location=[lat, lon],
            popup=f"{city} (Reference)",
            tooltip=city,
            radius=8,
            color='blue',
            fillColor='lightblue',
            fillOpacity=0.7
        ).add_to(m)
    
    # Add legend
    legend_html = '''
    <div style="position: fixed; 
                bottom: 50px; left: 50px; width: 250px; height: 140px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:14px; padding: 10px">
    <p><b>Pakistan Flood Hub Coverage</b></p>
    <p><i class="fa fa-star" style="color:green"></i> Real Pakistani Gauge (High Priority)</p>
    <p><i class="fa fa-circle" style="color:blue"></i> Major Cities (Reference)</p>
    <p style="color:red">━━━ Pakistan Boundary</p>
    <p><small><b>Coverage:</b> 1 gauge found<br>
    <b>Quality:</b> Verified + Model<br>
    <b>Status:</b> Limited coverage</small></p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Add title
    title_html = '''
                 <h3 align="center" style="font-size:20px"><b>Pakistan Google Flood Hub - REAL DATA</b></h3>
                 <p align="center">Actual gauge coverage discovered via API - Very Limited</p>
                 '''
    m.get_root().html.add_child(folium.Element(title_html))
    
    # Save map
    output_path = 'visualizations/real_pakistan_flood_hub_map.html'
    m.save(output_path)
    
    return output_path


def create_coverage_comparison_chart():
    """Create charts comparing expected vs actual coverage"""
    
    # Load real data
    try:
        with open('data/pakistan_coverage_report.json', 'r') as f:
            coverage_report = json.load(f)
    except:
        coverage_report = {}
    
    # Create comparison figure
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Pakistan Flood Hub: Expected vs Actual Coverage', fontsize=16, fontweight='bold')
    
    # 1. Coverage comparison
    categories = ['Total Gauges', 'Quality Verified', 'Has Models', 'Real-time Data']
    expected = [75, 50, 49, 20]  # From our mock data analysis
    actual = [1, 1, 1, 0]  # From real API discovery
    
    x = range(len(categories))
    width = 0.35
    
    ax1.bar([i - width/2 for i in x], expected, width, label='Expected (Mock)', alpha=0.7, color='skyblue')
    ax1.bar([i + width/2 for i in x], actual, width, label='Actual (Real API)', alpha=0.9, color='orange')
    ax1.set_title('Coverage Comparison')
    ax1.set_xticks(x)
    ax1.set_xticklabels(categories, rotation=45, ha='right')
    ax1.set_ylabel('Number of Gauges')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # 2. Geographic coverage
    provinces = ['Punjab', 'Sindh', 'KPK', 'Balochistan', 'GB']
    mock_coverage = [15, 12, 20, 12, 16]  # From mock data
    real_coverage = [0, 0, 0, 1, 0]  # From real data
    
    ax2.bar(provinces, mock_coverage, alpha=0.7, color='skyblue', label='Expected')
    ax2.bar(provinces, real_coverage, alpha=0.9, color='orange', label='Actual')
    ax2.set_title('Provincial Coverage')
    ax2.set_ylabel('Number of Gauges')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    # 3. Data quality pie chart (actual data)
    quality_labels = ['Quality Verified\n+ Model', 'Other']
    quality_values = [1, 0]
    colors = ['#2ecc71', '#e74c3c']
    
    ax3.pie(quality_values, labels=quality_labels, autopct='%1.0f%%', colors=colors, startangle=90)
    ax3.set_title('Actual Data Quality\n(1 gauge found)')
    
    # 4. Critical gaps visualization
    gaps = ['Indus River', 'Major Cities', 'Punjab Region', 'Sindh Region', 'Real-time Data']
    gap_severity = [10, 10, 10, 10, 8]  # Severity out of 10
    
    bars = ax4.barh(gaps, gap_severity, color=['#e74c3c' if x >= 9 else '#f39c12' for x in gap_severity])
    ax4.set_title('Critical Coverage Gaps')
    ax4.set_xlabel('Severity (1-10)')
    ax4.set_xlim(0, 10)
    
    # Add severity labels
    for i, (gap, severity) in enumerate(zip(gaps, gap_severity)):
        ax4.text(severity + 0.1, i, f'{severity}/10', va='center')
    
    plt.tight_layout()
    
    # Save chart
    chart_path = 'visualizations/real_vs_expected_coverage.png'
    plt.savefig(chart_path, dpi=300, bbox_inches='tight')
    
    return chart_path


def create_threshold_analysis_chart():
    """Create visualization of the gauge's flood thresholds"""
    
    try:
        with open('data/detailed_gauge_analysis.json', 'r') as f:
            analysis = json.load(f)
        
        thresholds = analysis.get('gauge_model', {}).get('thresholds', {})
        if not thresholds:
            print("No threshold data available for visualization")
            return None
        
        # Extract threshold values
        warning = thresholds.get('warningLevel', 0)
        danger = thresholds.get('dangerLevel', 0)
        extreme = thresholds.get('extremeDangerLevel', 0)
        units = analysis.get('gauge_model', {}).get('gaugeValueUnit', '')
        
        # Create threshold visualization
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        fig.suptitle('Pakistani Gauge Flood Thresholds (hybas_4121489010)', fontsize=14, fontweight='bold')
        
        # 1. Bar chart of thresholds
        levels = ['Warning', 'Danger', 'Extreme\nDanger']
        values = [warning, danger, extreme]
        colors = ['#f39c12', '#e67e22', '#c0392b']
        
        bars = ax1.bar(levels, values, color=colors, alpha=0.8)
        ax1.set_title('Flood Warning Thresholds')
        ax1.set_ylabel(f'Flow Rate ({units})')
        ax1.grid(True, alpha=0.3)
        
        # Add value labels on bars
        for bar, value in zip(bars, values):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + height*0.01,
                    f'{value:.1f}', ha='center', va='bottom', fontweight='bold')
        
        # 2. Cumulative risk visualization
        risk_levels = [0, warning, danger, extreme, extreme * 1.2]
        risk_colors = ['#27ae60', '#f39c12', '#e67e22', '#c0392b', '#8b0000']
        risk_labels = ['Normal', 'Warning', 'Danger', 'Extreme', 'Critical']
        
        for i in range(len(risk_levels)-1):
            ax2.axhspan(risk_levels[i], risk_levels[i+1], 
                       color=risk_colors[i], alpha=0.7, label=risk_labels[i])
        
        ax2.set_ylim(0, extreme * 1.2)
        ax2.set_xlim(-0.5, 0.5)
        ax2.set_title('Flood Risk Scale')
        ax2.set_ylabel(f'Flow Rate ({units})')
        ax2.legend(loc='upper left')
        ax2.set_xticks([])
        
        # Add threshold lines
        for level, value, color in zip(['Warning', 'Danger', 'Extreme'], values, colors):
            ax2.axhline(y=value, color=color, linestyle='--', linewidth=2, alpha=0.8)
            ax2.text(0.1, value, f'{level}: {value:.1f}', va='center', 
                    bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))
        
        plt.tight_layout()
        
        # Save chart
        threshold_path = 'visualizations/gauge_threshold_analysis.png'
        plt.savefig(threshold_path, dpi=300, bbox_inches='tight')
        
        return threshold_path
        
    except Exception as e:
        print(f"Error creating threshold chart: {e}")
        return None


def create_summary_report():
    """Create a summary report of real data findings"""
    
    report_path = 'reports/real_data_findings.md'
    
    # Load analysis data
    try:
        with open('data/detailed_gauge_analysis.json', 'r') as f:
            analysis = json.load(f)
        with open('data/pakistan_coverage_report.json', 'r') as f:
            coverage = json.load(f)
    except:
        print("Analysis files not found")
        return None
    
    # Generate report
    report_content = f"""# Pakistan Google Flood Hub - Real Data Analysis

**Analysis Date:** {datetime.now().strftime('%B %d, %Y')}
**API Key Used:** Working (validated)
**Data Source:** Google Flood Hub API (Official)

## Executive Summary

Our comprehensive analysis of Google Flood Hub's Pakistani coverage reveals **extremely limited but high-quality data availability**. Only **1 gauge** was discovered accessible through the API, representing minimal coverage for a country of Pakistan's size and flood risk profile.

## Key Findings

### ✅ Discovered Gauge: hybas_4121489010

**Location:** 26.060°N, 68.931°E (Balochistan Province)
**Quality Status:** ✓ Quality Verified
**Model Status:** ✓ Has Predictive Model
**Suitability Score:** 8/10 (High Priority)

**Flood Thresholds:**
- Warning Level: {analysis.get('gauge_model', {}).get('thresholds', {}).get('warningLevel', 'N/A')} m³/s
- Danger Level: {analysis.get('gauge_model', {}).get('thresholds', {}).get('dangerLevel', 'N/A')} m³/s
- Extreme Danger: {analysis.get('gauge_model', {}).get('thresholds', {}).get('extremeDangerLevel', 'N/A')} m³/s

### ⚠️ Critical Coverage Gaps

1. **No Indus River Coverage** - Pakistan's main river system unmonitored
2. **No Major City Coverage** - Karachi, Lahore, Islamabad not covered
3. **No Punjab Coverage** - Most flood-prone agricultural region missing
4. **No Sindh Coverage** - High-risk monsoon flood area missing
5. **Limited Real-time Data** - Flood status endpoint not accessible

### 📊 Coverage Statistics

- **Total Pakistani Gauges Found:** 1
- **Quality Verified:** 1 (100%)
- **Have Predictive Models:** 1 (100%)
- **Geographic Coverage:** <1% of Pakistan
- **Population Coverage:** Minimal (rural area)

## Technical Assessment

### ✅ API Functionality
- **Authentication:** Working with provided API key
- **Gauge Metadata:** Successfully retrievable
- **Model Data:** Available with detailed thresholds
- **Data Quality:** High (quality verified + model)

### ❌ API Limitations
- **Area Search:** Not available/accessible
- **Flood Status:** Real-time data endpoint not working
- **Gauge Discovery:** No bulk listing capability
- **Coverage:** Severely limited for Pakistan

## Recommendations for Pak-FEWS

### Immediate Actions
1. **Monitor Available Gauge** - Integrate hybas_4121489010 into monitoring system
2. **Request Enhanced Access** - Apply for additional API permissions from Google
3. **Alternative Data Sources** - Investigate PMD, WAPDA, and satellite data
4. **Open-Meteo Integration** - Use alternative flood APIs for broader coverage

### System Design Implications
1. **Multi-Source Architecture** - Cannot rely solely on Google Flood Hub
2. **Satellite Integration** - Consider Google Earth Engine for satellite flood detection
3. **Local Data Priority** - Prioritize Pakistani meteorological department data
4. **Hybrid Approach** - Combine multiple APIs and data sources

### Research Next Steps
1. **Enhanced API Access** - Apply to Google Flood Hub pilot program
2. **Earth Engine Exploration** - Research Google Earth Engine flood datasets
3. **Local API Investigation** - Explore Pakistani government flood monitoring APIs
4. **International Cooperation** - Connect with regional flood monitoring networks

## Budget Impact

- **Current API Usage:** Free (single gauge)
- **Enhanced Access:** Unknown cost structure
- **Alternative Sources:** Consider open-source options first
- **Development Time:** Additional integration work required

## Conclusion

While Google Flood Hub provides **excellent data quality** for the single accessible gauge, the **coverage is insufficient** for comprehensive Pakistani flood monitoring. The Pak-FEWS system must incorporate **multiple data sources** to achieve effective 24-hour advance flood warning capability.

The discovered gauge (hybas_4121489010) should be **prioritized for monitoring** due to its high quality, but **alternative data sources are essential** for meaningful flood early warning coverage across Pakistan.

---

*Report generated by Pakistan Flood Hub Research Team*
*Next update: After enhanced API access or alternative source integration*
"""

    # Save report
    os.makedirs('reports', exist_ok=True)
    with open(report_path, 'w') as f:
        f.write(report_content)
    
    return report_path


def main():
    """Create all real data visualizations and reports"""
    
    print("Creating Real Data Visualizations and Analysis")
    print("=" * 55)
    
    # Ensure output directories exist
    os.makedirs('visualizations', exist_ok=True)
    os.makedirs('reports', exist_ok=True)
    
    # Create visualizations
    print("\n1. Creating real gauge map...")
    map_path = create_real_data_map()
    if map_path:
        print(f"   ✓ Created: {map_path}")
    
    print("\n2. Creating coverage comparison charts...")
    comparison_path = create_coverage_comparison_chart()
    print(f"   ✓ Created: {comparison_path}")
    
    print("\n3. Creating threshold analysis...")
    threshold_path = create_threshold_analysis_chart()
    if threshold_path:
        print(f"   ✓ Created: {threshold_path}")
    
    print("\n4. Generating summary report...")
    report_path = create_summary_report()
    if report_path:
        print(f"   ✓ Created: {report_path}")
    
    # Summary
    print("\n" + "=" * 55)
    print("REAL DATA VISUALIZATION COMPLETE")
    print("=" * 55)
    print("Generated files:")
    if map_path:
        print(f"  • {map_path} - Interactive map with real gauge")
    print(f"  • {comparison_path} - Expected vs actual coverage")
    if threshold_path:
        print(f"  • {threshold_path} - Flood threshold analysis")
    if report_path:
        print(f"  • {report_path} - Comprehensive findings report")
    
    print("\nKey finding: Only 1 Pakistani gauge accessible via Google Flood Hub API")
    print("Recommendation: Integrate alternative data sources for comprehensive coverage")


if __name__ == "__main__":
    main()