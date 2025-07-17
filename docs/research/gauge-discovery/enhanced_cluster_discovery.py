#!/usr/bin/env python3
"""
Enhanced Cluster Discovery for Pakistan Gauges
Focus on finding gauge clusters around known successful gauges
"""

import os
import requests
import time
from datetime import datetime
from typing import List, Dict, Set

class EnhancedClusterDiscovery:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get('GOOGLE_FLOOD_HUB_API_KEY')
        self.base_url = 'https://floodforecasting.googleapis.com/v1'
        self.session = requests.Session()
        
        # Known successful gauges from our previous discoveries
        self.known_successful = [
            4121489010,  # Quality verified
            4120570410,  # Chitral
            4120567890,
            4121134230,
            4121159200,
            4120353670,
            4121451720,
            4121550980,
            4120786380,
            4120820400,
        ]
        
    def generate_cluster_candidates(self, center_id: int, radius: int = 1000) -> List[str]:
        """Generate candidate IDs around a successful gauge"""
        candidates = []
        
        # Dense testing around successful gauge
        for offset in range(-radius, radius + 1, 10):
            candidate_id = center_id + offset
            if 4100000000 <= candidate_id <= 4199999999:  # Valid Pakistan range
                candidates.append(f"hybas_{candidate_id}")
        
        return candidates
    
    def generate_pattern_variations(self, base_id: int) -> List[str]:
        """Generate variations based on ID patterns"""
        variations = []
        base_str = str(base_id)
        
        # Last digit variations
        for d in range(10):
            var_id = int(base_str[:-1] + str(d))
            variations.append(f"hybas_{var_id}")
        
        # Last two digit variations
        for d in range(100):
            var_id = int(base_str[:-2] + f"{d:02d}")
            variations.append(f"hybas_{var_id}")
        
        # Increment/decrement patterns
        increments = [1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 2000, 5000, 10000]
        for inc in increments:
            for direction in [-1, 1]:
                var_id = base_id + (direction * inc)
                if 4100000000 <= var_id <= 4199999999:
                    variations.append(f"hybas_{var_id}")
        
        return variations
    
    def test_gauge_batch(self, gauge_ids: List[str]) -> List[Dict]:
        """Test a batch of gauge IDs"""
        valid_gauges = []
        
        headers = {
            'X-goog-api-key': self.api_key,
            'Content-Type': 'application/json'
        }
        
        for i, gauge_id in enumerate(gauge_ids):
            try:
                gauge_url = f'{self.base_url}/gauges/{gauge_id}'
                response = self.session.get(gauge_url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    gauge_data = response.json()
                    quality_verified = gauge_data.get('qualityVerified', False)
                    status = "✓ VERIFIED" if quality_verified else "⚠ UNVERIFIED"
                    
                    print(f"[{i+1}/{len(gauge_ids)}] Found: {gauge_id} [{status}]")
                    
                    valid_gauges.append({
                        'gauge_id': gauge_id,
                        'quality_verified': quality_verified,
                        'location': gauge_data.get('location', {}),
                        'site_name': gauge_data.get('siteName', ''),
                        'river': gauge_data.get('river', ''),
                        'has_model': gauge_data.get('hasModel', False)
                    })
                elif i % 50 == 0:
                    print(f"[{i+1}/{len(gauge_ids)}] Tested {i+1}, found {len(valid_gauges)} valid")
                
                # Rate limiting
                if i % 10 == 0:
                    time.sleep(0.5)
                    
            except Exception as e:
                if i % 100 == 0:
                    print(f"[{i+1}/{len(gauge_ids)}] Some network errors (normal)")
                continue
        
        return valid_gauges
    
    def run_cluster_discovery(self):
        """Run enhanced cluster discovery around known gauges"""
        print("ENHANCED CLUSTER DISCOVERY")
        print("=" * 50)
        print(f"Testing clusters around {len(self.known_successful)} known gauges")
        
        all_candidates = set()
        all_valid_gauges = []
        
        for i, center_id in enumerate(self.known_successful):
            print(f"\n--- Cluster {i+1}/{len(self.known_successful)}: Around {center_id} ---")
            
            # Generate cluster candidates
            cluster_candidates = self.generate_cluster_candidates(center_id, radius=500)
            pattern_candidates = self.generate_pattern_variations(center_id)
            
            # Combine and deduplicate
            combined_candidates = set(cluster_candidates + pattern_candidates)
            new_candidates = combined_candidates - all_candidates
            all_candidates.update(combined_candidates)
            
            print(f"Generated {len(new_candidates)} new candidates for cluster {i+1}")
            
            # Test candidates
            if new_candidates:
                valid_gauges = self.test_gauge_batch(list(new_candidates))
                all_valid_gauges.extend(valid_gauges)
                print(f"Cluster {i+1} results: {len(valid_gauges)} valid gauges found")
            
            # Progress update
            print(f"Total progress: {len(all_valid_gauges)} valid gauges discovered so far")
        
        # Final summary
        print(f"\n{'='*50}")
        print("CLUSTER DISCOVERY COMPLETE")
        print(f"{'='*50}")
        print(f"Total candidates tested: {len(all_candidates)}")
        print(f"Total valid gauges found: {len(all_valid_gauges)}")
        
        if all_valid_gauges:
            verified_count = sum(1 for g in all_valid_gauges if g['quality_verified'])
            print(f"Quality verified: {verified_count}")
            print(f"Success rate: {len(all_valid_gauges)/len(all_candidates)*100:.2f}%")
            
            print("\nNewly discovered gauges:")
            for gauge in all_valid_gauges:
                status = "✓ VERIFIED" if gauge['quality_verified'] else "⚠ UNVERIFIED"
                print(f"  {gauge['gauge_id']} [{status}] - {gauge['site_name'] or 'Unnamed'}")
        
        # Save results
        import json
        results = {
            'discovery_date': datetime.now().isoformat(),
            'method': 'enhanced_cluster_discovery',
            'center_gauges': [f"hybas_{gid}" for gid in self.known_successful],
            'total_tested': len(all_candidates),
            'total_found': len(all_valid_gauges),
            'success_rate': len(all_valid_gauges)/len(all_candidates)*100 if all_candidates else 0,
            'discovered_gauges': all_valid_gauges
        }
        
        with open('cluster_discovery_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        # Save gauge IDs for import
        with open('cluster_discovered_gauge_ids.txt', 'w') as f:
            for gauge in all_valid_gauges:
                f.write(f"{gauge['gauge_id']}\n")
        
        print(f"\nResults saved to cluster_discovery_results.json")
        print(f"Gauge IDs saved to cluster_discovered_gauge_ids.txt")
        
        return all_valid_gauges

def main():
    discovery = EnhancedClusterDiscovery()
    
    if not discovery.api_key:
        print("Error: GOOGLE_FLOOD_HUB_API_KEY not found in environment")
        return
    
    # Run cluster discovery
    discovered_gauges = discovery.run_cluster_discovery()
    
    print(f"\nCLUSTER DISCOVERY SUMMARY:")
    print(f"Discovered {len(discovered_gauges)} new gauges")
    print(f"Previous total: 30 gauges")
    print(f"New total: {30 + len(discovered_gauges)} gauges")
    print(f"Remaining to find: {2391 - (30 + len(discovered_gauges))} gauges")
    print(f"Progress: {(30 + len(discovered_gauges))/2391*100:.1f}% complete")

if __name__ == "__main__":
    main()