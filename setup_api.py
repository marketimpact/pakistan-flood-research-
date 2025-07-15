#!/usr/bin/env python3
"""
Setup script for configuring Google Flood Hub API access
"""

import os
import sys
from pathlib import Path

def setup_api_key():
    """Interactive setup for Google Flood Hub API key"""
    
    print("🌊 Pakistan Flood Hub Analyzer - API Setup")
    print("=" * 50)
    
    # Check if already configured
    existing_key = os.getenv('GOOGLE_FLOOD_HUB_API_KEY')
    if existing_key:
        print(f"✅ API key already found in environment: {existing_key[:10]}...")
        response = input("Would you like to update it? (y/N): ")
        if response.lower() != 'y':
            print("Using existing API key.")
            return existing_key
    
    print("\n📋 To get your Google Flood Hub API key:")
    print("1. Go to: https://console.cloud.google.com/")
    print("2. Create or select a project")
    print("3. Enable the Google Flood Hub API")
    print("4. Go to 'APIs & Services' > 'Credentials'")
    print("5. Click 'Create Credentials' > 'API Key'")
    print("6. Copy the generated key")
    
    print("\n🔑 Enter your Google Flood Hub API key:")
    api_key = input("API Key: ").strip()
    
    if not api_key:
        print("❌ No API key provided. Exiting.")
        return None
    
    # Choose storage method
    print("\n💾 How would you like to store the API key?")
    print("1. Environment variable (recommended for production)")
    print("2. .env file (convenient for development)")
    print("3. Both")
    
    choice = input("Choose option (1-3): ").strip()
    
    if choice in ['1', '3']:
        # Set environment variable
        os.environ['GOOGLE_FLOOD_HUB_API_KEY'] = api_key
        print("✅ API key set in environment variable")
        
        # Provide instructions for permanent setup
        print("\n📝 To make this permanent, add to your shell profile:")
        print(f"export GOOGLE_FLOOD_HUB_API_KEY='{api_key}'")
    
    if choice in ['2', '3']:
        # Create .env file
        env_path = Path('.env')
        with open(env_path, 'w') as f:
            f.write(f"GOOGLE_FLOOD_HUB_API_KEY={api_key}\n")
        print(f"✅ API key saved to {env_path}")
        
        # Add .env to .gitignore if it exists
        gitignore_path = Path('.gitignore')
        if gitignore_path.exists():
            with open(gitignore_path, 'r') as f:
                content = f.read()
            if '.env' not in content:
                with open(gitignore_path, 'a') as f:
                    f.write('\n.env\n')
                print("✅ Added .env to .gitignore")
        else:
            with open(gitignore_path, 'w') as f:
                f.write('.env\n')
            print("✅ Created .gitignore with .env")
    
    return api_key

def test_api_connection():
    """Test the API connection"""
    print("\n🔍 Testing API connection...")
    
    try:
        from config import config
        
        if not config.is_configured():
            print("❌ API key not configured properly")
            return False
        
        import requests
        
        # Test with a simple API call
        url = f"{config.base_url}/v1/gauges:searchGaugesByArea"
        params = config.get_params({
            "area": "23.5,60.5,37.5,77.5"  # Pakistan bounds
        })
        
        print(f"Testing: {url}")
        response = requests.get(url, params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            gauge_count = len(data.get('gauges', []))
            print(f"✅ API connection successful!")
            print(f"📊 Found {gauge_count} gauges in Pakistan region")
            return True
        elif response.status_code == 401:
            print("❌ Authentication failed - check your API key")
            return False
        elif response.status_code == 403:
            print("❌ API access forbidden - ensure Flood Hub API is enabled")
            return False
        else:
            print(f"⚠️ API returned status {response.status_code}: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Network error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main setup process"""
    
    print("🚀 Starting API setup process...\n")
    
    # Setup API key
    api_key = setup_api_key()
    
    if api_key:
        # Test connection
        if test_api_connection():
            print("\n🎉 Setup completed successfully!")
            print("\nNext steps:")
            print("1. Run: python3 comprehensive_flood_analyzer.py")
            print("2. The system will now use live Google Flood Hub data")
            print("3. Check generated reports for real Pakistani gauge data")
        else:
            print("\n⚠️ Setup completed but API test failed")
            print("Please check your API key and try again")
    else:
        print("\n❌ Setup cancelled")
        print("You can run the system without an API key using sample data")

if __name__ == "__main__":
    main()