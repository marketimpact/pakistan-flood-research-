#!/usr/bin/env python3
"""
Quick start script for Pakistan Flood Hub Analysis
Handles API setup and runs comprehensive analysis
"""

import sys
import os
from pathlib import Path

def check_environment():
    """Check if environment is properly set up"""
    required_files = [
        'comprehensive_flood_analyzer.py',
        'config.py',
        'requirements.txt'
    ]
    
    missing_files = [f for f in required_files if not Path(f).exists()]
    if missing_files:
        print(f"❌ Missing required files: {missing_files}")
        return False
    
    # Check virtual environment
    if sys.prefix == sys.base_prefix:
        print("⚠️ Virtual environment not activated")
        print("Run: source venv/bin/activate")
        return False
    
    return True

def check_api_setup():
    """Check if API is configured"""
    try:
        from config import config
        return config.is_configured()
    except ImportError:
        return False

def main():
    """Main execution with setup checks"""
    
    print("🌊 Pakistan Flood Hub Analyzer")
    print("=" * 40)
    
    # Check environment
    if not check_environment():
        sys.exit(1)
    
    # Check API setup
    if not check_api_setup():
        print("🔧 API not configured. Running setup...")
        os.system("python3 setup_api.py")
        
        # Recheck after setup
        if not check_api_setup():
            print("\n⚠️ Proceeding with sample data (no API key)")
            response = input("Continue? (Y/n): ")
            if response.lower() == 'n':
                sys.exit(1)
    else:
        print("✅ API configured - using live Google Flood Hub data")
    
    # Run analysis
    print("\n🚀 Starting comprehensive flood analysis...")
    print("This may take a few minutes with live API data...\n")
    
    try:
        from comprehensive_flood_analyzer import main as run_analysis
        run_analysis()
    except KeyboardInterrupt:
        print("\n\n⏹️ Analysis interrupted by user")
    except Exception as e:
        print(f"\n❌ Error during analysis: {e}")
        print("Check logs for details")

if __name__ == "__main__":
    main()