#!/usr/bin/env python3
"""
Test script for HTTP/SSE server endpoints.
Tests both local and remote servers with different request formats.
"""
import asyncio
import httpx
import json
import sys


async def test_endpoint(base_url: str, api_key: str):
    """Test the /tools/call endpoint with different formats."""

    headers = {
        "X-API-Key": api_key,
        "Content-Type": "application/json"
    }

    print(f"\n{'='*60}")
    print(f"Testing: {base_url}")
    print(f"{'='*60}\n")

    # Test 1: Health check (no auth)
    print("1. Testing health check...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/health")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.json()}")
            print("   ✅ Health check passed\n")
    except Exception as e:
        print(f"   ❌ Health check failed: {e}\n")
        return

    # Test 2: List tools
    print("2. Testing list tools...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{base_url}/tools", headers=headers)
            print(f"   Status: {response.status_code}")
            tools = response.json()
            print(f"   Found {len(tools)} tools")
            print("   ✅ List tools passed\n")
    except Exception as e:
        print(f"   ❌ List tools failed: {e}\n")
        return

    # Test 3: Call tool with nested arguments (standard MCP format)
    print("3. Testing search_candidate with nested arguments...")
    test_email = "test@example.com"
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            payload = {
                "name": "search_candidate",
                "arguments": {
                    "email": test_email
                }
            }
            print(f"   Request: {json.dumps(payload, indent=2)}")
            response = await client.post(
                f"{base_url}/tools/call",
                headers=headers,
                json=payload
            )
            print(f"   Status: {response.status_code}")
            result = response.json()
            print(f"   Response: {json.dumps(result, indent=2)}")

            if response.status_code == 200 and result.get("success"):
                print("   ✅ Nested arguments format works\n")
            else:
                print(f"   ❌ Failed: {result.get('error', 'Unknown error')}\n")
    except Exception as e:
        print(f"   ❌ Request failed: {e}\n")

    # Test 4: Call tool with flat arguments (ChatGPT format)
    print("4. Testing search_candidate with flat arguments (ChatGPT style)...")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            payload = {
                "name": "search_candidate",
                "email": test_email
            }
            print(f"   Request: {json.dumps(payload, indent=2)}")
            response = await client.post(
                f"{base_url}/tools/call",
                headers=headers,
                json=payload
            )
            print(f"   Status: {response.status_code}")
            result = response.json()
            print(f"   Response: {json.dumps(result, indent=2)}")

            if response.status_code == 200 and result.get("success"):
                print("   ✅ Flat arguments format works\n")
            else:
                print(f"   ❌ Failed: {result.get('error', 'Unknown error')}\n")
    except Exception as e:
        print(f"   ❌ Request failed: {e}\n")

    # Test 5: Tool with no parameters
    print("5. Testing get_custom_fields_definitions (no params)...")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            payload = {
                "name": "get_custom_fields_definitions"
            }
            response = await client.post(
                f"{base_url}/tools/call",
                headers=headers,
                json=payload
            )
            print(f"   Status: {response.status_code}")
            result = response.json()
            if response.status_code == 200 and result.get("success"):
                print(f"   Found {len(result.get('result', []))} custom fields")
                print("   ✅ No-parameter tool works\n")
            else:
                print(f"   ❌ Failed: {result.get('error', 'Unknown error')}\n")
    except Exception as e:
        print(f"   ❌ Request failed: {e}\n")

    # Test 6: Tool with multiple parameters
    print("6. Testing update_candidate_stage (multiple params)...")
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Flat format
            payload = {
                "name": "update_candidate_stage",
                "email": test_email,
                "stage_name": "Test Stage"
            }
            print(f"   Request: {json.dumps(payload, indent=2)}")
            response = await client.post(
                f"{base_url}/tools/call",
                headers=headers,
                json=payload
            )
            print(f"   Status: {response.status_code}")
            result = response.json()

            if response.status_code == 200:
                print("   ✅ Multi-parameter tool works\n")
            else:
                print(f"   Result: {json.dumps(result, indent=2)}\n")
    except Exception as e:
        print(f"   ❌ Request failed: {e}\n")

    print(f"\n{'='*60}")
    print("Testing complete!")
    print(f"{'='*60}\n")


async def main():
    """Main test function."""
    if len(sys.argv) < 3:
        print("Usage: python test_http_endpoint.py <base_url> <api_key>")
        print("\nExamples:")
        print("  # Test local server:")
        print("  python test_http_endpoint.py http://localhost:8000 your_api_key")
        print("\n  # Test Render deployment:")
        print("  python test_http_endpoint.py https://your-app.onrender.com your_api_key")
        sys.exit(1)

    base_url = sys.argv[1].rstrip('/')
    api_key = sys.argv[2]

    await test_endpoint(base_url, api_key)


if __name__ == "__main__":
    asyncio.run(main())
