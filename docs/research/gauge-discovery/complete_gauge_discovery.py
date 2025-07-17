#!/usr/bin/env python3
"""
Complete Pakistan Gauge Discovery Strategy
Comprehensive approach to find all 2,391 Pakistan gauges
"""

import json
import time
import requests
from datetime import datetime
from typing import List, Dict, Set
import concurrent.futures
from threading import Lock
import os
import random

class CompleteGaugeDiscovery:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get('GOOGLE_FLOOD_HUB_API_KEY')
        self.base_url = 'https://floodforecasting.googleapis.com/v1'
        self.session = requests.Session()
        self.discovered_gauges = set()
        self.lock = Lock()
        
    def strategy_1_comprehensive_hybas_ranges(self) -> List[str]:
        """
        Strategy 1: Comprehensive HYBAS ID generation
        Based on Pakistan's complete basin structure
        """
        print("Strategy 1: Comprehensive HYBAS Range Coverage")
        
        gauge_ids = []
        
        # Pakistan HYBAS codes: 412 (Asia) + subregions
        # Expand beyond our previous narrow ranges
        base_codes = [
            412,  # Main Pakistan code
            413,  # Possible extended Pakistan
            411,  # Possible overlapping regions
        ]
        
        subregion_codes = list(range(0, 10))  # 0-9 for different subregions
        
        for base in base_codes:
            for subregion in subregion_codes:
                prefix = f"{base}{subregion}"
                
                # Generate comprehensive coverage within each subregion
                for i in range(1000000):  # 6 digits: 000000-999999
                    gauge_id = f"hybas_{prefix}{i:06d}"
                    gauge_ids.append(gauge_id)
                    
                    # Limit for testing
                    if len(gauge_ids) >= 50000:
                        break
                if len(gauge_ids) >= 50000:
                    break
            if len(gauge_ids) >= 50000:
                break
                
        print(f"Generated {len(gauge_ids)} comprehensive HYBAS IDs")
        return gauge_ids
    
    def strategy_2_sequential_search(self) -> List[str]:
        """
        Strategy 2: Sequential search in known working ranges
        More systematic than random generation
        """
        print("Strategy 2: Sequential Search in Working Ranges")
        
        gauge_ids = []
        
        # Based on production discoveries, focus on these ranges
        working_ranges = [
            (4120000000, 4120999999),  # Primary range
            (4121000000, 4121999999),  # Secondary range
            (4122000000, 4122999999),  # Extended range
            (4110000000, 4119999999),  # Alternative prefix
            (4130000000, 4139999999),  # Alternative prefix
        ]
        
        for start, end in working_ranges:
            # Sequential coverage with different step sizes
            step_sizes = [1, 10, 100, 1000, 10000]
            
            for step in step_sizes:
                for i in range(start, end, step):
                    gauge_ids.append(f"hybas_{i}")
                    
                    # Limit per range
                    if len(gauge_ids) >= 10000:
                        break
                if len(gauge_ids) >= 10000:
                    break
        
        print(f"Generated {len(gauge_ids)} sequential IDs")
        return gauge_ids
    
    def strategy_3_pattern_based_generation(self) -> List[str]:
        """
        Strategy 3: Pattern-based generation from known successful gauges
        """
        print("Strategy 3: Pattern-Based Generation")
        
        gauge_ids = []
        
        # Known successful patterns from our discoveries
        known_successful = [
            4121489010, 4120570410, 4120567890, 4121134230, 4121159200,
            4120353670, 4121451720, 4121550980, 4120786380, 4120820400
        ]
        
        for base_num in known_successful:
            # Generate variations around each successful gauge
            variations = [
                # Sequential neighbors
                *range(base_num - 1000, base_num + 1001, 10),
                # Pattern-based variations
                *[base_num + offset for offset in [-100000, -10000, -1000, -100, -10, -1, 
                                                   1, 10, 100, 1000, 10000, 100000]],
                # Digit pattern variations
                *[int(str(base_num)[:-1] + str(d)) for d in range(10)],  # Last digit
                *[int(str(base_num)[:-2] + f"{d:02d}") for d in range(100)],  # Last 2 digits
            ]
            
            for var in variations:
                if 4100000000 <= var <= 4199999999:  # Valid range
                    gauge_ids.append(f"hybas_{var}")
        
        # Remove duplicates
        gauge_ids = list(set(gauge_ids))
        print(f"Generated {len(gauge_ids)} pattern-based IDs")
        return gauge_ids
    
    def strategy_4_geographic_grid_search(self) -> List[str]:
        """
        Strategy 4: Geographic grid-based HYBAS generation
        Based on Pakistan's geographic extent
        """
        print("Strategy 4: Geographic Grid Search")
        
        gauge_ids = []
        
        # Pakistan bounding box: 23.5°N-37.5°N, 60.5°E-77.8°E
        # HYBAS codes are geographically structured
        
        # Hypothetical HYBAS structure for Pakistan regions
        regional_codes = {
            # Northern Pakistan (Kashmir, GB, Northern KPK)
            'north': [(4121000000, 4121999999), (4131000000, 4131999999)],
            # Central Pakistan (Punjab, Central KPK)
            'central': [(4120000000, 4120999999), (4130000000, 4130999999)],
            # Southern Pakistan (Sindh, Balochistan)
            'south': [(4122000000, 4122999999), (4132000000, 4132999999)],
        }
        
        for region, ranges in regional_codes.items():
            for start, end in ranges:
                # Grid-based sampling
                samples_per_region = 5000
                step = (end - start) // samples_per_region
                
                for i in range(start, end, step):
                    gauge_ids.append(f"hybas_{i}")
        
        print(f"Generated {len(gauge_ids)} geographic grid IDs")
        return gauge_ids
    
    def test_gauge_batch(self, gauge_ids: List[str], batch_size: int = 50) -> List[Dict]:
        """
        Test a batch of gauge IDs efficiently
        """
        valid_gauges = []
        
        print(f"Testing {len(gauge_ids)} gauge IDs in batches of {batch_size}...")
        
        def test_single_gauge(gauge_id: str) -> Dict:
            try:
                headers = {'X-goog-api-key': self.api_key, 'Content-Type': 'application/json'}
                gauge_url = f'{self.base_url}/gauges/{gauge_id}'
                response = self.session.get(gauge_url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    gauge_data = response.json()
                    return {
                        'gauge_id': gauge_id,
                        'data': gauge_data,
                        'quality_verified': gauge_data.get('qualityVerified', False),
                        'location': gauge_data.get('location', {}),
                    }
                return None
            except:
                return None
        
        # Process in batches with threading
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            for i in range(0, len(gauge_ids), batch_size):
                batch = gauge_ids[i:i+batch_size]
                
                futures = [executor.submit(test_single_gauge, gid) for gid in batch]
                
                for future in concurrent.futures.as_completed(futures):
                    result = future.result()
                    if result:
                        valid_gauges.append(result)
                        status = "✓ VERIFIED" if result['quality_verified'] else "⚠ UNVERIFIED"
                        print(f"Found: {result['gauge_id']} [{status}]")
                
                # Progress and rate limiting
                print(f"Tested {min(i+batch_size, len(gauge_ids))}/{len(gauge_ids)}, found {len(valid_gauges)} valid")
                time.sleep(1)  # Rate limiting
        
        return valid_gauges
    
    def run_comprehensive_discovery(self, max_per_strategy: int = 5000):
        """
        Run all discovery strategies
        """
        print("COMPREHENSIVE PAKISTAN GAUGE DISCOVERY")
        print("=" * 60)
        
        if not self.api_key:
            print("Error: API key required")
            return
        
        strategies = [
            ("Comprehensive HYBAS", self.strategy_1_comprehensive_hybas_ranges),
            ("Sequential Search", self.strategy_2_sequential_search),
            ("Pattern-Based", self.strategy_3_pattern_based_generation),
            ("Geographic Grid", self.strategy_4_geographic_grid_search),
        ]
        
        all_valid_gauges = []
        
        for strategy_name, strategy_func in strategies:
            print(f"\n{'='*20} {strategy_name} {'='*20}")
            
            # Generate candidates
            candidate_ids = strategy_func()
            
            # Limit for testing
            test_ids = candidate_ids[:max_per_strategy]
            
            # Test candidates
            valid_gauges = self.test_gauge_batch(test_ids)
            all_valid_gauges.extend(valid_gauges)
            
            print(f"{strategy_name} Results: {len(valid_gauges)} valid out of {len(test_ids)} tested")
            
            # Save intermediate results
            self.save_results(all_valid_gauges, f"discovery_results_{strategy_name.lower().replace(' ', '_')}.json")
        
        # Final summary
        print(f"\n{'='*60}")
        print("DISCOVERY COMPLETE")
        print(f"{'='*60}")
        print(f"Total valid gauges discovered: {len(all_valid_gauges)}")
        
        # Remove duplicates
        unique_gauges = {g['gauge_id']: g for g in all_valid_gauges}
        print(f"Unique gauges: {len(unique_gauges)}")
        
        verified_count = sum(1 for g in unique_gauges.values() if g['quality_verified'])
        print(f"Quality verified: {verified_count}")
        
        # Save final results
        self.save_results(list(unique_gauges.values()), "complete_discovery_results.json")
        
        return list(unique_gauges.values())
    
    def save_results(self, gauges: List[Dict], filename: str):
        """Save discovery results"""
        results = {
            'discovery_date': datetime.now().isoformat(),
            'total_found': len(gauges),
            'quality_verified': sum(1 for g in gauges if g['quality_verified']),
            'gauges': gauges
        }
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"Results saved to {filename}")

def main():
    discovery = CompleteGaugeDiscovery()
    
    # Run comprehensive discovery
    discovered_gauges = discovery.run_comprehensive_discovery(max_per_strategy=1000)
    
    print(f"\nDiscovered {len(discovered_gauges)} total gauges")
    print(f"Still need to find {2391 - len(discovered_gauges)} more gauges to reach 2,391 target")

if __name__ == "__main__":
    main()