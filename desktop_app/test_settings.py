"""
Test Settings Loading - vibeshield_pro.py API Key Display
"""

import json
import os

CONFIG_FILE = "config.json"

def test_config_load():
    """Test if config loads correctly"""
    print("=" * 60)
    print("TESTING: Config Loading & API Key Display")
    print("=" * 60)
    
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
        
        print("\n✓ Config file found and loaded")
        print(f"\nAPI Key from config: {config.get('openrouter_api_key', 'NOT FOUND')}")
        
        api_key = config.get('openrouter_api_key', '')
        
        if api_key:
            print(f"\n✓ API Key exists!")
            print(f"  Display format: {api_key[:10]}...{api_key[-4:]}")
            print(f"  Status: GREEN (Success)")
        else:
            print(f"\n✗ API Key is empty!")
            print(f"  Status: RED (Danger)")
        
        print(f"\nProject Path: {config.get('project_path', 'NOT SET')}")
        print(f"Target URL: {config.get('target_url', 'NOT SET')}")
        
    else:
        print("\n✗ Config file not found!")
        print("  Creating default config...")
        config = {
            'openrouter_api_key': '',
            'target_url': 'http://localhost:8000',
            'project_path': ''
        }
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=2)
        print("  ✓ Default config created")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    test_config_load()
