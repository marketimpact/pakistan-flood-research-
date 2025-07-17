#!/usr/bin/env python3
"""
Analyze known Pakistan gauge IDs to identify patterns
"""

import json
import re
from collections import defaultdict, Counter

# Known working gauge IDs from various sources
KNOWN_GAUGES = [
    # From our database discoveries
    "hybas_4121489010",  # Quality verified
    "hybas_4120570410",  # Chitral
    "hybas_4120567890",
    "hybas_4120983530",
    "hybas_4120857010",
    "hybas_4120962950",
    "hybas_4120573410",
    "hybas_4120915890",
    "hybas_4120121470",
    "hybas_4120760570",
    "hybas_4120558140",
    "hybas_4120210000",
    "hybas_4120124220",
    "hybas_4120492590",
    "hybas_4120038810",
    "hybas_4120115500",
    "hybas_4120092960",
    "hybas_4120954970",
    "hybas_4120890520",
    "hybas_4120127960",
    "hybas_4120502440",
    "hybas_4120449360",
    "hybas_4120604970",
    "hybas_4120073530",
    "hybas_4120031450",
    "hybas_4120873950",
    "hybas_4120825520",
    "hybas_4120476650",
]

def analyze_gauge_patterns():
    """Analyze patterns in known gauge IDs"""
    
    print("PAKISTAN GAUGE ID PATTERN ANALYSIS")
    print("=" * 50)
    
    # Extract numeric parts
    numeric_ids = []
    for gauge_id in KNOWN_GAUGES:
        match = re.match(r'hybas_(\d+)', gauge_id)
        if match:
            numeric_ids.append(match.group(1))
    
    print(f"\nTotal known gauges: {len(KNOWN_GAUGES)}")
    print(f"Quality verified: 1 (hybas_4121489010)")
    
    # Analyze prefixes
    prefix_counts = Counter()
    for num_id in numeric_ids:
        # Check different prefix lengths
        prefix_counts[num_id[:3]] += 1  # First 3 digits
        prefix_counts[num_id[:4]] += 1  # First 4 digits
        prefix_counts[num_id[:5]] += 1  # First 5 digits
    
    print("\nPrefix Analysis:")
    for prefix, count in sorted(prefix_counts.items(), key=lambda x: (-x[1], x[0])):
        if count > 1:
            print(f"  {prefix}xxxxx: {count} gauges")
    
    # Analyze number ranges
    numbers = [int(n) for n in numeric_ids]
    print(f"\nNumeric Range Analysis:")
    print(f"  Min: {min(numbers)} ({min(numbers):,})")
    print(f"  Max: {max(numbers)} ({max(numbers):,})")
    print(f"  Range: {max(numbers) - min(numbers):,}")
    
    # Group by millions
    million_groups = defaultdict(list)
    for num in numbers:
        million_key = num // 1_000_000
        million_groups[million_key].append(num)
    
    print("\nDistribution by million:")
    for million, nums in sorted(million_groups.items()):
        print(f"  {million}xxxxxx: {len(nums)} gauges")
    
    # Analyze last digits patterns
    last_digits = Counter()
    for num_id in numeric_ids:
        last_digits[num_id[-2:]] += 1
    
    print("\nCommon endings (last 2 digits):")
    for ending, count in sorted(last_digits.items(), key=lambda x: -x[1])[:10]:
        if count > 1:
            print(f"  ...{ending}: {count} gauges")
    
    # Look for sequential patterns
    sorted_numbers = sorted(numbers)
    gaps = []
    for i in range(1, len(sorted_numbers)):
        gap = sorted_numbers[i] - sorted_numbers[i-1]
        if gap < 100000:  # Reasonable gap
            gaps.append(gap)
    
    if gaps:
        avg_gap = sum(gaps) / len(gaps)
        print(f"\nSequential Analysis:")
        print(f"  Average gap between close gauges: {avg_gap:,.0f}")
        print(f"  Smallest gap: {min(gaps):,}")
        print(f"  Largest reasonable gap: {max(gaps):,}")
    
    # HYBAS pattern insights
    print("\nHYBAS ID Structure Insights:")
    print("  Format: hybas_AABCCCCCC")
    print("  AA = 41 (Asia region code)")
    print("  B = 2 (Pakistan subregion)")
    print("  CCCCCC = Specific basin/gauge identifier")
    print("\nPakistan HYBAS range: 4120000000 - 4129999999")
    
    # Suggest search strategies
    print("\nRecommended Search Strategies:")
    print("1. Systematic search in high-density ranges:")
    for million, nums in sorted(million_groups.items()):
        if len(nums) > 5:
            min_val = min(nums)
            max_val = max(nums)
            print(f"   - Range {min_val:,} to {max_val:,} (found {len(nums)} gauges)")
    
    print("\n2. Focus on common patterns:")
    print("   - IDs ending in: 10, 20, 30, 40, 50, 60, 70, 80, 90")
    print("   - IDs with round numbers (xxx000, xxx500)")
    
    # Export for further analysis
    export_data = {
        "known_gauges": KNOWN_GAUGES,
        "numeric_ids": numeric_ids,
        "statistics": {
            "total": len(KNOWN_GAUGES),
            "quality_verified": 1,
            "min_id": min(numbers),
            "max_id": max(numbers),
            "prefixes": dict(prefix_counts)
        }
    }
    
    with open("known_gauges_analysis.json", "w") as f:
        json.dump(export_data, f, indent=2)
    
    print("\nAnalysis exported to: known_gauges_analysis.json")

if __name__ == "__main__":
    analyze_gauge_patterns()