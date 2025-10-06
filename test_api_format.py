#!/usr/bin/env python3
"""
Quick test to verify Viterbit API accepts our candidatures/search payload format
"""
import os
import asyncio
import httpx

VITERBIT_API_KEY = os.getenv("VITERBIT_API_KEY")
BASE_URL = "https://api.viterbit.com/v1"

async def test_search_format():
    """Test the candidatures/search API format"""

    if not VITERBIT_API_KEY:
        print("❌ VITERBIT_API_KEY not set")
        return

    headers = {
        "X-API-Key": VITERBIT_API_KEY,
        "Content-Type": "application/json"
    }

    # Test 1: Search with current_stage filter (should work)
    print("\n1️⃣ Testing search with current_stage filter...")
    payload1 = {
        "filters": {
            "groups": [
                {
                    "operator": "and",
                    "filters": [
                        {
                            "field": "current_stage__name",
                            "operator": "equals",
                            "value": "Match"
                        }
                    ]
                }
            ]
        },
        "page": 1,
        "page_size": 10,
        "search": None
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{BASE_URL}/candidatures/search",
                json=payload1,
                headers=headers,
                timeout=10.0
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Success! Found {len(data.get('data', []))} candidatures")
            else:
                print(f"   ❌ Error: {response.text}")
        except Exception as e:
            print(f"   ❌ Exception: {e}")

    # Test 2: Search for "Preseleccionado" stage
    print("\n2️⃣ Testing search with Preseleccionado stage...")
    payload2 = {
        "filters": {
            "groups": [
                {
                    "operator": "and",
                    "filters": [
                        {
                            "field": "current_stage__name",
                            "operator": "equals",
                            "value": "Preseleccionado"
                        }
                    ]
                }
            ]
        },
        "page": 1,
        "page_size": 10,
        "search": None
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                f"{BASE_URL}/candidatures/search",
                json=payload2,
                headers=headers,
                timeout=10.0
            )
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ Success! Found {len(data.get('data', []))} candidatures")
            else:
                print(f"   ❌ Error: {response.text}")
        except Exception as e:
            print(f"   ❌ Exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_search_format())
