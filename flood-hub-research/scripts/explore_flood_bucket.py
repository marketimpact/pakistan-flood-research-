#!/usr/bin/env python3
"""
Explore the Google Cloud Storage flood data bucket
Find files relevant to Pakistan
"""

import urllib.request
import json

# Based on the screenshot, files use negative longitudes for some reason
# Let's try different coordinate patterns
TEST_COORDINATES = [
    # Standard Pakistan coordinates
    (35.000, 70.000),   # Northern Pakistan
    (30.000, 70.000),   # Central Pakistan
    (25.000, 70.000),   # Southern Pakistan
    
    # Try negative patterns seen in screenshot
    (0.000, -50.019),   # From screenshot
    (35.000, -70.000),  # Negative longitude test
    
    # Try variations
    (36.385, 72.206),   # Exact Chitral
    (36.000, 72.000),   # Rounded Chitral
    (35.000, 72.000),   # Chitral tile variant
]

BASE_URL = "https://storage.googleapis.com/flood-forecasting/inundation_history/data/"

def try_download(lat, lon, precision=3):
    """Try downloading with different coordinate formats"""
    attempts = [
        f"inundation_history_{lat:.{precision}f}_{lon:.{precision}f}.geojson",
        f"inundation_history_{lat}_{lon}.geojson",
        f"inundation_history_{int(lat)}.000_{int(lon)}.000.geojson",
    ]
    
    for filename in attempts:
        url = BASE_URL + filename
        try:
            with urllib.request.urlopen(url) as response:
                # Just check if it exists
                print(f"✓ FOUND: {filename}")
                return True
        except:
            continue
    
    return False

print("🔍 EXPLORING GOOGLE FLOOD DATA BUCKET")
print("="*60)

# First, let's try to understand the pattern from the screenshot
print("\n1. Testing coordinate patterns:")

found_files = []
for lat, lon in TEST_COORDINATES:
    print(f"\nTrying {lat}, {lon}:")
    if try_download(lat, lon):
        found_files.append((lat, lon))
    else:
        print(f"   ✗ Not found")

# Try systematic search around Pakistan
print("\n\n2. Systematic search around Pakistan region:")
print("(This may take a while...)")

# Broader search with 5-degree increments
for lat in range(20, 40, 5):
    for lon in range(60, 80, 5):
        if try_download(float(lat), float(lon)):
            found_files.append((lat, lon))

# Also try negative longitudes (based on screenshot pattern)
for lat in range(-90, 90, 10):
    for lon in range(-180, -40, 10):
        if lat == 0 and lon == -50:  # Skip the one we know exists
            continue
        if try_download(float(lat), float(lon), precision=3):
            found_files.append((lat, lon))
            # If we find one, check nearby
            for dlat in [-5, 5]:
                for dlon in [-5, 5]:
                    try_download(float(lat + dlat), float(lon + dlon), precision=3)

print("\n" + "="*60)
print(f"SUMMARY: Found {len(found_files)} accessible files")
if found_files:
    print("\nAccessible coordinates:")
    for lat, lon in found_files:
        print(f"  - {lat}, {lon}")
        
print("\n💡 Note: The bucket may use a different coordinate system or access pattern")
print("   The screenshot shows files like 'inundation_history_-0.000_-50.019.geojson'")
print("   which suggests Western Hemisphere data or a different indexing scheme")