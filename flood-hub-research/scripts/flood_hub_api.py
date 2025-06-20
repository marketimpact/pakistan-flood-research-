#!/usr/bin/env python3
"""
Google Flood Hub API Wrapper
Provides methods to interact with Google Flood Hub API endpoints
"""

import requests
import time
import json
from typing import Dict, List, Optional, Any
from datetime import datetime


class FloodHubAPI:
    """Client for Google Flood Hub API"""
    
    BASE_URL = "https://floodforecasting.googleapis.com/v1"
    
    def __init__(self, api_key: Optional[str] = None, rate_limit_delay: float = 0.1):
        """
        Initialize API client
        
        Args:
            api_key: Google Cloud API key for authentication
            rate_limit_delay: Delay between requests in seconds
        """
        self.session = requests.Session()
        self.api_key = api_key
        self.rate_limit_delay = rate_limit_delay
        self.last_request_time = 0
        
    def _rate_limit(self):
        """Enforce rate limiting between requests"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - time_since_last)
        self.last_request_time = time.time()
        
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Dict:
        """
        Make API request with error handling
        
        Args:
            endpoint: API endpoint path
            params: Query parameters
            
        Returns:
            JSON response as dictionary
            
        Raises:
            requests.exceptions.RequestException: On API errors
        """
        self._rate_limit()
        
        url = f"{self.BASE_URL}/{endpoint}"
        
        # Add API key to parameters or headers (try both methods)
        if params is None:
            params = {}
            
        headers = {}
        if self.api_key:
            # Try header-based authentication first
            headers['X-goog-api-key'] = self.api_key
            # Also add as parameter as fallback
            params['key'] = self.api_key
        
        try:
            response = self.session.get(url, params=params, headers=headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API Error: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response content: {e.response.text}")
            raise
            
    def search_gauges_by_area(self,
                              min_lat: Optional[float] = None,
                              max_lat: Optional[float] = None,
                              min_lon: Optional[float] = None,
                              max_lon: Optional[float] = None) -> List[Dict]:
        """
        Search for gauges by geographical area
        Try different endpoint formats to find the correct one
        """
        # Try different endpoint formats
        endpoints_to_try = [
            'gauges',
            'gauges:search',
            'gauges:searchByArea',
            'gauges:searchGaugesByArea'
        ]
        
        params = {}
        if all(x is not None for x in [min_lat, max_lat, min_lon, max_lon]):
            # Try different parameter naming conventions
            param_formats = [
                {
                    'minLatitude': min_lat,
                    'maxLatitude': max_lat,
                    'minLongitude': min_lon,
                    'maxLongitude': max_lon
                },
                {
                    'min_lat': min_lat,
                    'max_lat': max_lat,
                    'min_lon': min_lon,
                    'max_lon': max_lon
                },
                {
                    'bbox': f"{min_lon},{min_lat},{max_lon},{max_lat}"
                }
            ]
        else:
            param_formats = [{}]
            
        for endpoint in endpoints_to_try:
            for param_format in param_formats:
                try:
                    print(f"Trying endpoint: {endpoint} with params: {param_format}")
                    response = self._make_request(endpoint, param_format)
                    
                    # If we get here, the request succeeded
                    print(f"✓ Success with endpoint: {endpoint}")
                    
                    if isinstance(response, dict) and 'gauges' in response:
                        return response['gauges']
                    elif isinstance(response, list):
                        return response
                    else:
                        print(f"Response structure: {type(response)}")
                        if isinstance(response, dict):
                            print(f"Response keys: {list(response.keys())}")
                        return []
                        
                except Exception as e:
                    print(f"Failed: {endpoint} - {str(e)[:100]}")
                    continue
                    
        print("All endpoint attempts failed")
        return []
            
    def get_gauges(self, 
                   min_lat: Optional[float] = None,
                   max_lat: Optional[float] = None,
                   min_lon: Optional[float] = None,
                   max_lon: Optional[float] = None) -> List[Dict]:
        """
        Get list of gauges, optionally filtered by bounding box
        Fallback to search_gauges_by_area if needed
        """
        return self.search_gauges_by_area(min_lat, max_lat, min_lon, max_lon)
            
    def get_gauge_details(self, gauge_id: str) -> Dict:
        """
        Get detailed information for a specific gauge
        
        Args:
            gauge_id: Gauge identifier
            
        Returns:
            Gauge details dictionary
        """
        return self._make_request(f'gauges/{gauge_id}')
        
    def get_flood_status(self, gauge_id: Optional[str] = None) -> Dict:
        """
        Get current flood status/predictions
        
        Args:
            gauge_id: Optional gauge ID to filter by
            
        Returns:
            Flood status data
        """
        params = {'gaugeId': gauge_id} if gauge_id else {}
        return self._make_request('floodStatus', params)
        
    def get_gauge_models(self, gauge_id: str) -> Dict:
        """
        Get model/threshold data for a gauge
        
        Args:
            gauge_id: Gauge identifier
            
        Returns:
            Model data including thresholds
        """
        return self._make_request(f'gaugeModels/{gauge_id}')
        
    def test_connection(self) -> bool:
        """
        Test API connection with a simple request
        
        Returns:
            True if connection successful
        """
        try:
            print("Testing API connection without geographic filter...")
            # Try to get gauges without geographic filtering first
            gauges = self.search_gauges_by_area()
            
            if gauges:
                print(f"✓ API connection successful. Found {len(gauges)} gauges total.")
                print(f"Sample gauge: {json.dumps(gauges[0], indent=2)}")
                return True
            else:
                print("No gauges returned, but no error occurred")
                return False
                
        except Exception as e:
            print(f"Connection test failed: {e}")
            return False


def main():
    """Test API connection when run directly"""
    print("Testing Google Flood Hub API connection...")
    
    # Use provided API key
    api_key = "AIzaSyB0d7jLuqXjDJW_BQxOyCrBVt97zse7S-M"
    api = FloodHubAPI(api_key=api_key)
    
    if api.test_connection():
        print("\n✓ API wrapper is working correctly")
        
        # Test Pakistan bounding box
        print("\nTesting Pakistan bounding box query...")
        pak_gauges = api.get_gauges(
            min_lat=23.0,
            max_lat=37.0,
            min_lon=60.0,
            max_lon=77.0
        )
        print(f"Found {len(pak_gauges)} gauges in Pakistan bounding box")
        if pak_gauges:
            print(f"Sample gauge: {json.dumps(pak_gauges[0], indent=2)}")
    else:
        print("\n✗ API connection failed")


if __name__ == "__main__":
    main()