#!/usr/bin/env python3
"""
Web Scrape Google Flood Hub for Complete Pakistan Gauge List
This approach extracts gauge IDs directly from the web interface
"""

import requests
import json
import re
import time
from datetime import datetime
from typing import List, Dict, Set
from urllib.parse import urljoin, urlparse
import os

class FloodHubScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.found_gauge_ids = set()
        
    def scrape_flood_hub_map(self):
        """
        Scrape the main Flood Hub map interface for Pakistan gauges
        """
        print("Scraping Google Flood Hub map interface...")
        
        # Pakistan bounding box for URL parameters
        pak_bounds = {
            'lat_min': 23.5, 'lat_max': 37.5,
            'lng_min': 60.5, 'lng_max': 77.8
        }
        
        # Try different zoom levels and regions
        zoom_levels = [6, 7, 8, 9, 10]
        
        for zoom in zoom_levels:
            for lat in [25, 30, 35]:  # Sample latitudes across Pakistan
                for lng in [65, 70, 75]:  # Sample longitudes across Pakistan
                    url = f"https://sites.research.google/floods/l/{lat}/{lng}/{zoom}"
                    
                    try:
                        print(f"Checking region: lat={lat}, lng={lng}, zoom={zoom}")
                        response = self.session.get(url, timeout=30)
                        
                        if response.status_code == 200:
                            # Look for gauge IDs in the response
                            gauge_ids = self.extract_gauge_ids_from_html(response.text)
                            self.found_gauge_ids.update(gauge_ids)
                            print(f"Found {len(gauge_ids)} gauge IDs in this region")
                        
                        time.sleep(2)  # Rate limiting
                        
                    except Exception as e:
                        print(f"Error scraping {url}: {e}")
                        continue
        
        print(f"Total unique gauge IDs found: {len(self.found_gauge_ids)}")
        return list(self.found_gauge_ids)
    
    def extract_gauge_ids_from_html(self, html_content: str) -> Set[str]:
        """
        Extract gauge IDs from HTML content
        """
        gauge_ids = set()
        
        # Pattern for HYBAS gauge IDs
        patterns = [
            r'hybas_\d{10}',  # Standard HYBAS format
            r'"gaugeId":\s*"(hybas_\d+)"',  # JSON format
            r"'gaugeId':\s*'(hybas_\d+)'",  # JSON format with single quotes
            r'/gauges/(hybas_\d+)',  # URL format
            r'gauge.*?(hybas_\d{10})',  # General gauge references
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, html_content, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple):
                    gauge_id = match[0]
                else:
                    gauge_id = match
                
                # Validate format
                if gauge_id.startswith('hybas_') and len(gauge_id.split('_')[1]) >= 10:
                    gauge_ids.add(gauge_id)
        
        return gauge_ids
    
    def scrape_api_documentation(self):
        """
        Check API documentation for example gauge IDs
        """
        print("Scraping API documentation for gauge examples...")
        
        doc_urls = [
            "https://developers.google.com/flood-forecasting",
            "https://sites.research.google/gr/floodforecasting/",
            "https://support.google.com/flood-hub/",
        ]
        
        for url in doc_urls:
            try:
                response = self.session.get(url, timeout=30)
                if response.status_code == 200:
                    gauge_ids = self.extract_gauge_ids_from_html(response.text)
                    self.found_gauge_ids.update(gauge_ids)
                    print(f"Found {len(gauge_ids)} gauge IDs in documentation: {url}")
                time.sleep(1)
            except Exception as e:
                print(f"Error scraping documentation {url}: {e}")
        
        return list(self.found_gauge_ids)
    
    def search_github_repositories(self):
        """
        Search GitHub for repositories that might contain Pakistan gauge lists
        """
        print("Searching GitHub for gauge references...")
        
        search_terms = [
            "Pakistan flood gauges",
            "Google Flood Hub Pakistan", 
            "hybas_412",
            "Pakistan flood monitoring",
            "Google flood forecasting Pakistan"
        ]
        
        # Note: This would require GitHub API token for full access
        # For now, just search public repositories
        
        for term in search_terms:
            try:
                # GitHub search API (limited without token)
                url = f"https://api.github.com/search/code?q={term}"
                response = self.session.get(url, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    for item in data.get('items', []):
                        # Get the file content
                        if 'url' in item:
                            file_response = self.session.get(item['url'])
                            if file_response.status_code == 200:
                                file_data = file_response.json()
                                content = file_data.get('content', '')
                                
                                # Decode base64 if needed
                                if file_data.get('encoding') == 'base64':
                                    import base64
                                    content = base64.b64decode(content).decode('utf-8')
                                
                                gauge_ids = self.extract_gauge_ids_from_html(content)
                                self.found_gauge_ids.update(gauge_ids)
                
                time.sleep(5)  # Rate limiting for GitHub API
                
            except Exception as e:
                print(f"Error searching GitHub for '{term}': {e}")
                continue
        
        return list(self.found_gauge_ids)
    
    def scrape_research_papers(self):
        """
        Search academic papers and reports for gauge references
        """
        print("Searching research papers for gauge references...")
        
        # Common academic search engines and repositories
        search_urls = [
            "https://scholar.google.com/scholar?q=Pakistan+flood+monitoring+Google+Flood+Hub",
            "https://www.researchgate.net/search?q=Pakistan%20flood%20gauges",
            # Add more academic sources as needed
        ]
        
        for url in search_urls:
            try:
                response = self.session.get(url, timeout=30)
                if response.status_code == 200:
                    gauge_ids = self.extract_gauge_ids_from_html(response.text)
                    self.found_gauge_ids.update(gauge_ids)
                    print(f"Found {len(gauge_ids)} gauge IDs in research: {url}")
                time.sleep(5)  # Be respectful with academic sites
            except Exception as e:
                print(f"Error scraping research {url}: {e}")
        
        return list(self.found_gauge_ids)
    
    def run_comprehensive_scraping(self):
        """
        Run all scraping methods
        """
        print("COMPREHENSIVE WEB SCRAPING FOR PAKISTAN GAUGES")
        print("=" * 60)
        
        methods = [
            ("Flood Hub Map Interface", self.scrape_flood_hub_map),
            ("API Documentation", self.scrape_api_documentation),
            ("GitHub Repositories", self.search_github_repositories),
            ("Research Papers", self.scrape_research_papers),
        ]
        
        for method_name, method_func in methods:
            print(f"\n{'='*20} {method_name} {'='*20}")
            
            try:
                method_func()
                print(f"Total unique gauges after {method_name}: {len(self.found_gauge_ids)}")
            except Exception as e:
                print(f"Error in {method_name}: {e}")
        
        # Final results
        final_gauges = list(self.found_gauge_ids)
        
        print(f"\n{'='*60}")
        print("SCRAPING COMPLETE")
        print(f"{'='*60}")
        print(f"Total unique gauge IDs found: {len(final_gauges)}")
        
        # Save results
        results = {
            'scraping_date': datetime.now().isoformat(),
            'total_found': len(final_gauges),
            'gauge_ids': final_gauges,
            'methods_used': [name for name, _ in methods]
        }
        
        with open('scraped_gauge_ids.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        # Also save as simple text file
        with open('scraped_gauge_ids.txt', 'w') as f:
            for gauge_id in final_gauges:
                f.write(f"{gauge_id}\n")
        
        print("Results saved to scraped_gauge_ids.json and scraped_gauge_ids.txt")
        
        return final_gauges

def main():
    scraper = FloodHubScraper()
    
    # Run comprehensive scraping
    discovered_gauges = scraper.run_comprehensive_scraping()
    
    print(f"\nDiscovered {len(discovered_gauges)} gauge IDs via web scraping")
    
    if len(discovered_gauges) > 0:
        print("\nSample discovered gauges:")
        for gauge_id in discovered_gauges[:10]:
            print(f"  {gauge_id}")
        
        if len(discovered_gauges) > 10:
            print(f"  ... and {len(discovered_gauges) - 10} more")
    
    print(f"\nNext step: Validate these {len(discovered_gauges)} gauge IDs against the API")

if __name__ == "__main__":
    main()