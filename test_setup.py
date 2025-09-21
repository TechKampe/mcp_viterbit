#!/usr/bin/env python3
"""
Test script to verify Viterbit MCP server setup.

This script tests the basic functionality without running the full MCP server.
"""
import asyncio
import os
import sys
from dotenv import load_dotenv

# Add the current directory to Python path so we can import our modules
sys.path.insert(0, os.path.dirname(__file__))

from viterbit_client import ViterbitClient, ViterbitAPIError
from config import VITERBIT_API_KEY


async def test_setup():
    """Test the Viterbit MCP server setup."""
    print("🧪 Testing Viterbit MCP Server Setup...")
    print("=" * 50)

    # Load environment variables
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_file):
        load_dotenv(env_file)
        print("✅ Loaded .env file")
    else:
        print("⚠️  No .env file found - using system environment variables")

    # Check API key
    if not VITERBIT_API_KEY:
        print("❌ VITERBIT_API_KEY not found in environment variables")
        print("   Please set it in your .env file or environment")
        return False

    print("✅ VITERBIT_API_KEY found")

    # Test client initialization
    try:
        client = ViterbitClient()
        print("✅ ViterbitClient initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize ViterbitClient: {e}")
        return False

    # Test API connection (optional - only if we want to make a real API call)
    try:
        print("\n🌐 Testing API connection...")
        # Test with a simple API call that doesn't require specific data
        result = await client.get_custom_fields_definitions()
        if result is not None:
            print("✅ Successfully connected to Viterbit API")
            print(f"   Retrieved {len(result.get('data', []))} custom field definitions")
        else:
            print("⚠️  API call succeeded but returned no data")
    except ViterbitAPIError as e:
        print(f"❌ Viterbit API error: {e}")
        print("   Check your API key and network connection")
        return False
    except Exception as e:
        print(f"❌ Unexpected error during API test: {e}")
        return False

    print("\n🎉 All tests passed! Your Viterbit MCP server is ready to use.")
    print("\nTo run the MCP server:")
    print("   python server.py")
    print("\nTo add to Claude Desktop, use this config:")
    print('   "viterbit": {')
    print('     "command": "python",')
    print(f'     "args": ["{os.path.abspath("server.py")}"],')
    print('     "env": {')
    print(f'       "VITERBIT_API_KEY": "{VITERBIT_API_KEY[:8]}..."')
    print('     }')
    print('   }')

    return True


if __name__ == "__main__":
    success = asyncio.run(test_setup())
    sys.exit(0 if success else 1)