#!/usr/bin/env python3
"""
Test script for candidature stage tracking functionality.
"""
import asyncio
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from viterbit_client import ViterbitClient

async def main():
    """Test the new candidature stage tracking features."""
    print("Testing Viterbit Candidature Stage Tracking...")

    # Check if we have API key
    if not os.getenv("VITERBIT_API_KEY"):
        print("❌ VITERBIT_API_KEY environment variable not set")
        return

    try:
        client = ViterbitClient()
        print("✅ Viterbit client initialized")

        # Test 1: Get stage history for the example candidature
        test_candidature_id = "68d51d1ad47000542104aaa2"
        print(f"\n🔍 Testing stage history for candidature: {test_candidature_id}")

        result = await client.get_candidature_with_stage_history(test_candidature_id)
        if result:
            print("✅ Successfully retrieved candidature with stage history")
            stages = result.get("stages_history", [])
            print(f"📊 Found {len(stages)} stage transitions:")

            for i, stage in enumerate(stages, 1):
                stage_name = stage.get("stage_name", "Unknown")
                start_at = stage.get("start_at", "Unknown")
                print(f"   {i}. {stage_name} -> {start_at}")
        else:
            print("❌ Failed to retrieve stage history")

        # Test 2: Count candidatures changed to a specific stage
        print(f"\n📈 Testing count functionality for September 2025...")
        count = await client.count_candidatures_changed_to_stage("Match", 2025, 9)
        print(f"✅ Candidatures changed to 'Match' in September 2025: {count}")

        # Test 3: Get full list of candidatures changed to a specific stage
        print(f"\n📝 Testing full list retrieval for September 2025...")
        candidatures = await client.get_candidatures_changed_to_stage("Match", 2025, 9)
        print(f"✅ Retrieved {len(candidatures)} candidatures that changed to 'Match'")

        if candidatures:
            print("Sample results:")
            for i, candidature in enumerate(candidatures[:3], 1):  # Show first 3
                print(f"   {i}. ID: {candidature.get('candidature_id')} -> {candidature.get('stage_change_date')}")

        print("\n🎉 All tests completed successfully!")

    except Exception as e:
        print(f"❌ Error during testing: {e}")

if __name__ == "__main__":
    asyncio.run(main())