#!/usr/bin/env python3
"""
Test Generated Gauge IDs Against Google Flood Hub API
This script validates our systematically generated gauge IDs
"""

import json
import time
import requests
from datetime import datetime
from typing import Dict, List, Optional
import concurrent.futures
from threading import Lock
import os

class GaugeValidator:
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.environ.get('GOOGLE_FLOOD_HUB_API_KEY')
        self.base_url = 'https://floodforecasting.googleapis.com/v1'
        self.session = requests.Session()
        self.results = {
            'valid_gauges': [],
            'invalid_gauges': [],
            'errors': [],
            'statistics': {}
        }
        self.lock = Lock()
        
    def test_gauge_id(self, gauge_id: str) -> Dict:
        """Test a single gauge ID against the API"""
        try:
            headers = {
                'X-goog-api-key': self.api_key,
                'Content-Type': 'application/json'
            }
            
            # Test gauge endpoint
            gauge_url = f'{self.base_url}/gauges/{gauge_id}'
            response = self.session.get(gauge_url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                gauge_data = response.json()
                
                # Try to get threshold data
                threshold_data = None
                try:
                    threshold_url = f'{self.base_url}/gaugeModels/{gauge_id}'
                    threshold_response = self.session.get(threshold_url, headers=headers, timeout=10)
                    if threshold_response.status_code == 200:
                        threshold_data = threshold_response.json()
                except:
                    pass
                
                result = {
                    'gauge_id': gauge_id,
                    'status': 'valid',
                    'gauge_data': gauge_data,
                    'threshold_data': threshold_data,
                    'location': gauge_data.get('location', {}),
                    'quality_verified': gauge_data.get('qualityVerified', False),
                    'has_model': gauge_data.get('hasModel', False),
                    'river': gauge_data.get('river', ''),
                    'site_name': gauge_data.get('siteName', ''),
                    'timestamp': datetime.now().isoformat()
                }
                
                with self.lock:
                    self.results['valid_gauges'].append(result)
                    
                return result
                
            else:
                with self.lock:
                    self.results['invalid_gauges'].append({
                        'gauge_id': gauge_id,
                        'status_code': response.status_code,
                        'timestamp': datetime.now().isoformat()
                    })
                    
                return None
                
        except Exception as e:
            with self.lock:
                self.results['errors'].append({
                    'gauge_id': gauge_id,
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                })
            return None
    
    def test_gauge_batch(self, gauge_ids: List[str], batch_size: int = 10, delay: float = 0.1):
        """Test a batch of gauge IDs with rate limiting"""
        print(f"Testing {len(gauge_ids)} gauge IDs...")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=batch_size) as executor:
            futures = []
            
            for i, gauge_id in enumerate(gauge_ids):
                future = executor.submit(self.test_gauge_id, gauge_id)
                futures.append(future)
                
                # Rate limiting
                if i % batch_size == 0 and i > 0:
                    time.sleep(delay)
                    
                # Progress reporting
                if i % 100 == 0:
                    print(f"Submitted {i}/{len(gauge_ids)} requests...")
            
            # Wait for all futures to complete
            for i, future in enumerate(concurrent.futures.as_completed(futures)):
                if i % 100 == 0:
                    print(f"Completed {i}/{len(futures)} requests...")
                    
                try:
                    result = future.result()
                    if result:
                        status = "✓ VERIFIED" if result['quality_verified'] else "⚠ UNVERIFIED"
                        print(f"Found: {result['gauge_id']} [{status}]")
                except Exception as e:
                    print(f"Error in future: {e}")
    
    def load_gauge_ids_from_file(self, filename: str) -> List[str]:
        """Load gauge IDs from various file formats"""
        gauge_ids = []
        
        try:
            if filename.endswith('.json'):
                with open(filename, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, dict) and 'potential_gauges' in data:
                        gauge_ids = data['potential_gauges']
                    elif isinstance(data, list):
                        gauge_ids = data
                        
            elif filename.endswith('.txt'):
                with open(filename, 'r') as f:
                    gauge_ids = [line.strip() for line in f if line.strip()]
                    
            print(f"Loaded {len(gauge_ids)} gauge IDs from {filename}")
            return gauge_ids
            
        except Exception as e:
            print(f"Error loading gauge IDs: {e}")
            return []
    
    def save_results(self, filename: str = None):
        """Save validation results to file"""
        if not filename:
            filename = f"gauge_validation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Calculate statistics
        total_tested = len(self.results['valid_gauges']) + len(self.results['invalid_gauges']) + len(self.results['errors'])
        valid_count = len(self.results['valid_gauges'])
        verified_count = sum(1 for g in self.results['valid_gauges'] if g['quality_verified'])
        model_count = sum(1 for g in self.results['valid_gauges'] if g['has_model'])
        
        self.results['statistics'] = {
            'total_tested': total_tested,
            'valid_gauges': valid_count,
            'invalid_gauges': len(self.results['invalid_gauges']),
            'errors': len(self.results['errors']),
            'quality_verified': verified_count,
            'has_model': model_count,
            'success_rate': (valid_count / total_tested * 100) if total_tested > 0 else 0,
            'verification_rate': (verified_count / valid_count * 100) if valid_count > 0 else 0,
            'test_date': datetime.now().isoformat()
        }
        
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\nValidation Results Saved to: {filename}")
        print(f"Total Tested: {total_tested}")
        print(f"Valid Gauges: {valid_count} ({self.results['statistics']['success_rate']:.1f}%)")
        print(f"Quality Verified: {verified_count} ({self.results['statistics']['verification_rate']:.1f}%)")
        print(f"With Model: {model_count}")
        
        # Save just the valid gauge IDs for easy import
        valid_ids = [g['gauge_id'] for g in self.results['valid_gauges']]
        valid_ids_file = filename.replace('.json', '_valid_ids.txt')
        with open(valid_ids_file, 'w') as f:
            for gauge_id in valid_ids:
                f.write(f"{gauge_id}\n")
        
        print(f"Valid gauge IDs saved to: {valid_ids_file}")
    
    def print_summary(self):
        """Print a summary of findings"""
        print("\n" + "="*60)
        print("GAUGE VALIDATION SUMMARY")
        print("="*60)
        
        valid_gauges = self.results['valid_gauges']
        
        if valid_gauges:
            print(f"\nFound {len(valid_gauges)} valid gauges:")
            
            # Group by quality status
            verified = [g for g in valid_gauges if g['quality_verified']]
            unverified = [g for g in valid_gauges if not g['quality_verified']]
            
            if verified:
                print(f"\n✓ QUALITY VERIFIED ({len(verified)}):")
                for gauge in verified:
                    loc = gauge['location']
                    print(f"  {gauge['gauge_id']}: {gauge['site_name'] or 'Unnamed'} "
                          f"({loc.get('latitude', 'N/A')}, {loc.get('longitude', 'N/A')})")
            
            if unverified:
                print(f"\n⚠ UNVERIFIED ({len(unverified)}):")
                for gauge in unverified[:10]:  # Show first 10
                    loc = gauge['location']
                    print(f"  {gauge['gauge_id']}: {gauge['site_name'] or 'Unnamed'} "
                          f"({loc.get('latitude', 'N/A')}, {loc.get('longitude', 'N/A')})")
                if len(unverified) > 10:
                    print(f"  ... and {len(unverified) - 10} more")
        
        print(f"\nTotal gauges found: {len(valid_gauges)}")
        print(f"Success rate: {self.results['statistics']['success_rate']:.1f}%")

def main():
    """Main execution function"""
    print("PAKISTAN GAUGE ID VALIDATION")
    print("="*50)
    
    # Initialize validator
    validator = GaugeValidator()
    
    if not validator.api_key:
        print("Error: GOOGLE_FLOOD_HUB_API_KEY not found in environment")
        return
    
    # Load gauge IDs to test
    gauge_ids = validator.load_gauge_ids_from_file("gauge_ids_to_test.txt")
    
    if not gauge_ids:
        print("No gauge IDs to test. Generate them first with systematic_gauge_discovery.py")
        return
    
    # Test the gauge IDs
    start_time = time.time()
    validator.test_gauge_batch(gauge_ids, batch_size=5, delay=0.2)
    end_time = time.time()
    
    print(f"\nValidation completed in {end_time - start_time:.1f} seconds")
    
    # Save results and print summary
    validator.save_results()
    validator.print_summary()

if __name__ == "__main__":
    main()