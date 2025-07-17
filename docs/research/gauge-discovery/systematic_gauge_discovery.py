#!/usr/bin/env python3
"""
Systematic Pakistan Gauge Discovery
Based on HYBAS patterns and known gauge analysis
"""

import json
import time
from datetime import datetime

class PakistanGaugeDiscovery:
    def __init__(self):
        self.known_gauges = self._load_known_gauges()
        self.potential_gauges = set()
        
    def _load_known_gauges(self):
        """Load known gauges from our analysis"""
        try:
            with open("known_gauges_analysis.json", "r") as f:
                data = json.load(f)
                return set(data["known_gauges"])
        except:
            return set()
    
    def generate_systematic_ids(self):
        """Generate gauge IDs using multiple strategies"""
        print("SYSTEMATIC PAKISTAN GAUGE ID GENERATION")
        print("=" * 50)
        
        strategies = [
            self._strategy_1_round_numbers,
            self._strategy_2_incremental_search,
            self._strategy_3_basin_patterns,
            self._strategy_4_ending_patterns,
            self._strategy_5_density_areas,
            self._strategy_6_river_systems,
        ]
        
        for strategy in strategies:
            strategy()
        
        # Remove already known gauges
        new_potential = self.potential_gauges - self.known_gauges
        
        print(f"\nSummary:")
        print(f"  Known gauges: {len(self.known_gauges)}")
        print(f"  Total potential IDs generated: {len(self.potential_gauges)}")
        print(f"  New IDs to test: {len(new_potential)}")
        
        return sorted(list(new_potential))
    
    def _strategy_1_round_numbers(self):
        """Generate IDs with round numbers (multiples of 10, 100, 1000)"""
        print("\nStrategy 1: Round numbers...")
        count = 0
        
        # Multiples of 10000
        for i in range(4120000000, 4122000000, 10000):
            self.potential_gauges.add(f"hybas_{i}")
            count += 1
        
        # Multiples of 1000 in high-density areas
        for base in [4120000000, 4120100000, 4120200000, 4120500000, 4120800000, 4120900000]:
            for offset in range(0, 100000, 1000):
                self.potential_gauges.add(f"hybas_{base + offset}")
                count += 1
        
        print(f"  Generated {count} round number IDs")
    
    def _strategy_2_incremental_search(self):
        """Search incrementally around known gauges"""
        print("\nStrategy 2: Incremental search around known gauges...")
        count = 0
        
        for gauge in self.known_gauges:
            base_id = int(gauge.split('_')[1])
            
            # Search ±100 around each known gauge
            for offset in range(-100, 101, 10):
                new_id = base_id + offset
                if 4120000000 <= new_id <= 4129999999:
                    self.potential_gauges.add(f"hybas_{new_id}")
                    count += 1
        
        print(f"  Generated {count} incremental IDs")
    
    def _strategy_3_basin_patterns(self):
        """Generate IDs based on major river basins"""
        print("\nStrategy 3: Basin-based patterns...")
        count = 0
        
        # Major basins in Pakistan (hypothetical HYBAS sub-codes)
        basin_ranges = {
            "Indus Upper": (4120100000, 4120200000),
            "Indus Lower": (4120200000, 4120300000),
            "Jhelum": (4120300000, 4120400000),
            "Chenab": (4120400000, 4120500000),
            "Ravi": (4120500000, 4120600000),
            "Sutlej": (4120600000, 4120700000),
            "Kabul": (4120700000, 4120800000),
            "Swat": (4120800000, 4120900000),
            "Coastal": (4120900000, 4121000000),
        }
        
        for basin, (start, end) in basin_ranges.items():
            # Sample key points in each basin
            step = (end - start) // 100
            for i in range(start, end, step):
                self.potential_gauges.add(f"hybas_{i}")
                count += 1
        
        print(f"  Generated {count} basin-based IDs")
    
    def _strategy_4_ending_patterns(self):
        """Generate IDs with common ending patterns"""
        print("\nStrategy 4: Common ending patterns...")
        count = 0
        
        # Common endings from analysis: 10, 50, 70, 90, 20, 60
        common_endings = [10, 20, 30, 40, 50, 60, 70, 80, 90, 00]
        
        # Generate for each 10000 block in active range
        for base in range(4120000000, 4121000000, 10000):
            for hundred in range(0, 10000, 100):
                for ending in common_endings:
                    gauge_id = base + hundred + ending
                    self.potential_gauges.add(f"hybas_{gauge_id}")
                    count += 1
        
        print(f"  Generated {count} pattern-based IDs")
    
    def _strategy_5_density_areas(self):
        """Focus on areas with high gauge density"""
        print("\nStrategy 5: High-density area search...")
        count = 0
        
        # Areas with multiple known gauges
        density_ranges = [
            (4120000000, 4120100000),  # 4 known gauges
            (4120100000, 4120200000),  # 4 known gauges
            (4120500000, 4120600000),  # 5 known gauges
            (4120800000, 4120900000),  # 4 known gauges
            (4120900000, 4121000000),  # 4 known gauges
        ]
        
        for start, end in density_ranges:
            # More intensive search in these areas
            for i in range(start, end, 100):
                self.potential_gauges.add(f"hybas_{i}")
                count += 1
        
        print(f"  Generated {count} high-density area IDs")
    
    def _strategy_6_river_systems(self):
        """Generate IDs based on major river confluences and cities"""
        print("\nStrategy 6: River system key points...")
        count = 0
        
        # Key hydrological points (hypothetical)
        key_points = [
            # Major confluences
            4120250000,  # Panjnad (5 rivers confluence)
            4120350000,  # Jhelum-Chenab confluence
            4120450000,  # Ravi-Chenab confluence
            4120550000,  # Sutlej-Chenab confluence
            4120750000,  # Kabul-Indus confluence
            
            # Major cities on rivers
            4120150000,  # Lahore region
            4120175000,  # Multan region
            4120225000,  # Hyderabad region
            4120275000,  # Karachi region
            4120325000,  # Faisalabad region
            4120375000,  # Rawalpindi region
            4120425000,  # Peshawar region
            4120475000,  # Quetta region
        ]
        
        for point in key_points:
            # Generate IDs around key points
            for offset in range(-5000, 5001, 1000):
                gauge_id = point + offset
                if 4120000000 <= gauge_id <= 4129999999:
                    self.potential_gauges.add(f"hybas_{gauge_id}")
                    count += 1
        
        print(f"  Generated {count} river system IDs")
    
    def export_results(self, filename="potential_gauges.json"):
        """Export potential gauge IDs for testing"""
        new_potential = sorted(list(self.potential_gauges - self.known_gauges))
        
        export_data = {
            "generation_date": datetime.now().isoformat(),
            "known_gauges": sorted(list(self.known_gauges)),
            "potential_gauges": new_potential[:5000],  # Limit to first 5000 for testing
            "statistics": {
                "known_count": len(self.known_gauges),
                "generated_count": len(self.potential_gauges),
                "new_to_test": len(new_potential),
                "export_limit": min(5000, len(new_potential))
            }
        }
        
        with open(filename, "w") as f:
            json.dump(export_data, f, indent=2)
        
        print(f"\nExported to {filename}")
        print(f"Ready to test {export_data['statistics']['export_limit']} new gauge IDs")

def main():
    discovery = PakistanGaugeDiscovery()
    discovery.generate_systematic_ids()
    discovery.export_results()
    
    # Also create a simple text file with gauge IDs for easy processing
    new_potential = sorted(list(discovery.potential_gauges - discovery.known_gauges))
    with open("gauge_ids_to_test.txt", "w") as f:
        for gauge_id in new_potential[:5000]:
            f.write(f"{gauge_id}\n")
    
    print("\nNext steps:")
    print("1. Run test_gauge_ids.py to validate these IDs against Google Flood Hub API")
    print("2. Web search for additional gauge references")
    print("3. Check Pakistan meteorological and water management websites")

if __name__ == "__main__":
    main()