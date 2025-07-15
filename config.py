#!/usr/bin/env python3
"""
Configuration file for Pakistan Flood Hub Analyzer
Store your API credentials and settings here
"""

import os
from typing import Optional

class FloodHubConfig:
    """Configuration management for Google Flood Hub API"""
    
    def __init__(self):
        # Try to get API key from environment variable first, then fallback options
        self.api_key = self._get_api_key()
        
        # API endpoints - CORRECTED URL
        self.base_url = "https://floodforecasting.googleapis.com"
        
        # Pakistan geographical bounds
        self.pakistan_bounds = {
            "min_lat": 23.5,
            "max_lat": 37.5,
            "min_lon": 60.5,
            "max_lon": 77.5
        }
        
        # Rate limiting settings
        self.requests_per_minute = 60
        self.batch_size = 50
        self.max_retries = 3
        self.retry_delay_seconds = 30
        
        # Sync settings
        self.sync_interval_hours = 6
        self.auto_sync_enabled = True
    
    def _get_api_key(self) -> Optional[str]:
        """Get API key from various sources in order of preference"""
        
        # 1. Environment variable (most secure)
        api_key = os.getenv('GOOGLE_FLOOD_HUB_API_KEY')
        if api_key:
            return api_key
        
        # 2. Environment variable (alternative name)
        api_key = os.getenv('FLOOD_API_KEY')
        if api_key:
            return api_key
        
        # 3. Local config file (if exists)
        try:
            with open('.env', 'r') as f:
                for line in f:
                    if line.startswith('GOOGLE_FLOOD_HUB_API_KEY='):
                        return line.split('=', 1)[1].strip()
        except FileNotFoundError:
            pass
        
        # 4. Return None if no key found
        return None
    
    def is_configured(self) -> bool:
        """Check if API is properly configured"""
        return self.api_key is not None
    
    def get_headers(self) -> dict:
        """Get HTTP headers for API requests"""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Pakistan-Flood-Analyzer/1.0"
        }
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        return headers
    
    def get_params(self, additional_params: dict = None) -> dict:
        """Get query parameters for API requests"""
        params = {}
        
        if self.api_key:
            params["key"] = self.api_key
        
        if additional_params:
            params.update(additional_params)
        
        return params

# Global config instance
config = FloodHubConfig()