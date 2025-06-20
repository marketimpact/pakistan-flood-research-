#!/usr/bin/env python3
"""
Create Demo Coverage Map
Visualizes gauge locations on an interactive map
"""

import pandas as pd
import folium
from folium import plugins
import json


def create_coverage_map():
    """Create interactive map showing gauge coverage"""
    
    # Load processed gauge data
    df = pd.read_csv('data/processed_gauge_inventory.csv')
    
    # Pakistan center coordinates
    center_lat = 30.3753
    center_lon = 69.3451
    
    # Create map
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=6,
        tiles='OpenStreetMap'
    )
    
    # Define colors for different gauge types
    def get_gauge_color(row):
        if row['qualityVerified'] and row['hasModel']:
            return 'green'  # Best quality
        elif row['hasModel']:
            return 'orange'  # Has model but not verified
        elif row['qualityVerified']:
            return 'blue'   # Verified but no model
        else:
            return 'red'    # Neither verified nor has model
    
    def get_gauge_icon(row):
        if row['qualityVerified'] and row['hasModel']:
            return 'star'
        elif row['hasModel']:
            return 'play'
        elif row['qualityVerified']:
            return 'ok'
        else:
            return 'remove'
    
    # Add gauges to map
    for idx, row in df.iterrows():
        if pd.notna(row['latitude']) and pd.notna(row['longitude']):
            
            # Create popup text
            popup_text = f"""
            <b>Gauge ID:</b> {row['gaugeId']}<br>
            <b>Location:</b> {row['siteName']}<br>
            <b>River:</b> {row['river'] if row['river'] else 'Unknown'}<br>
            <b>Province:</b> {row['province']}<br>
            <b>Source:</b> {row['source']}<br>
            <b>Quality Verified:</b> {'Yes' if row['qualityVerified'] else 'No'}<br>
            <b>Has Model:</b> {'Yes' if row['hasModel'] else 'No'}<br>
            <b>Coordinates:</b> {row['latitude']:.4f}, {row['longitude']:.4f}
            """
            
            # Add marker
            folium.Marker(
                location=[row['latitude'], row['longitude']],
                popup=folium.Popup(popup_text, max_width=300),
                tooltip=f"{row['gaugeId']} - {row['siteName']}",
                icon=folium.Icon(
                    color=get_gauge_color(row),
                    icon=get_gauge_icon(row),
                    prefix='glyphicon'
                )
            ).add_to(m)
    
    # Add legend
    legend_html = '''
    <div style="position: fixed; 
                bottom: 50px; left: 50px; width: 200px; height: 120px; 
                background-color: white; border:2px solid grey; z-index:9999; 
                font-size:14px; padding: 10px">
    <p><b>Gauge Quality Legend</b></p>
    <p><i class="fa fa-star" style="color:green"></i> Quality Verified + Model</p>
    <p><i class="fa fa-play" style="color:orange"></i> Has Model Only</p>
    <p><i class="fa fa-ok" style="color:blue"></i> Quality Verified Only</p>
    <p><i class="fa fa-remove" style="color:red"></i> Basic Gauge</p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Add province boundaries (approximate)
    province_bounds = {
        'Punjab': [[27.7, 69.3], [33.0, 75.4]],
        'Sindh': [[23.5, 66.5], [28.5, 71.1]],
        'Khyber Pakhtunkhwa': [[31.0, 69.2], [36.0, 74.0]],
        'Balochistan': [[24.5, 60.5], [32.5, 70.3]],
        'Gilgit-Baltistan': [[34.5, 72.5], [37.0, 77.0]]
    }
    
    # Add province rectangles
    for province, bounds in province_bounds.items():
        folium.Rectangle(
            bounds=bounds,
            popup=province,
            tooltip=province,
            fill=False,
            color='gray',
            weight=2,
            opacity=0.5
        ).add_to(m)
    
    # Add title
    title_html = '''
                 <h3 align="center" style="font-size:20px"><b>Pakistan Flood Hub Gauge Coverage</b></h3>
                 <p align="center">Demo visualization showing gauge distribution and quality</p>
                 '''
    m.get_root().html.add_child(folium.Element(title_html))
    
    # Save map
    output_path = 'visualizations/demo_coverage_map.html'
    m.save(output_path)
    
    return output_path, len(df)


def create_summary_charts():
    """Create summary statistics charts"""
    import matplotlib.pyplot as plt
    import seaborn as sns
    
    # Load data
    df = pd.read_csv('data/processed_gauge_inventory.csv')
    
    # Set style
    plt.style.use('default')
    sns.set_palette("husl")
    
    # Create figure with subplots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    fig.suptitle('Pakistan Flood Hub Gauge Analysis', fontsize=16, fontweight='bold')
    
    # 1. Gauges by Province
    province_counts = df['province'].value_counts()
    ax1.bar(range(len(province_counts)), province_counts.values)
    ax1.set_title('Gauges by Province')
    ax1.set_xticks(range(len(province_counts)))
    ax1.set_xticklabels(province_counts.index, rotation=45, ha='right')
    ax1.set_ylabel('Number of Gauges')
    
    # 2. Quality Status Pie Chart
    quality_counts = df['qualityVerified'].value_counts()
    ax2.pie(quality_counts.values, labels=['Not Verified', 'Quality Verified'], autopct='%1.1f%%')
    ax2.set_title('Quality Verification Status')
    
    # 3. Model Availability
    model_counts = df['hasModel'].value_counts()
    ax3.pie(model_counts.values, labels=['No Model', 'Has Model'], autopct='%1.1f%%')
    ax3.set_title('Predictive Model Availability')
    
    # 4. Data Sources
    source_counts = df['source'].value_counts()
    ax4.bar(range(len(source_counts)), source_counts.values)
    ax4.set_title('Gauges by Data Source')
    ax4.set_xticks(range(len(source_counts)))
    ax4.set_xticklabels(source_counts.index, rotation=45, ha='right')
    ax4.set_ylabel('Number of Gauges')
    
    plt.tight_layout()
    
    # Save chart
    chart_path = 'visualizations/demo_analysis_charts.png'
    plt.savefig(chart_path, dpi=300, bbox_inches='tight')
    
    return chart_path


def main():
    """Create visualizations"""
    print("Creating Pakistan Flood Hub Demo Visualizations")
    print("=" * 50)
    
    # Create map
    print("1. Creating interactive coverage map...")
    map_path, gauge_count = create_coverage_map()
    print(f"   ✓ Created map with {gauge_count} gauges: {map_path}")
    
    # Create charts
    print("2. Creating summary charts...")
    chart_path = create_summary_charts()
    print(f"   ✓ Created charts: {chart_path}")
    
    print("\n" + "=" * 50)
    print("VISUALIZATIONS CREATED:")
    print(f"• {map_path} - Interactive map")
    print(f"• {chart_path} - Summary charts")
    print("\nOpen the HTML file in your browser to view the interactive map!")
    print("=" * 50)


if __name__ == "__main__":
    import os
    os.makedirs('visualizations', exist_ok=True)
    main()