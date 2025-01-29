#!/usr/bin/env python3

import os
from raspberry_pi_code.services.api.thingspeak import ThingSpeakAPI

def test_thingspeak():
    print("\nTesting ThingSpeak Connection:")
    print("-" * 30)
    
    # Get API key from environment
    api_key = os.getenv('THINGSPEAK_API_KEY')
    if not api_key:
        print("ERROR: ThingSpeak API key not found in environment variables!")
        print("Please set THINGSPEAK_API_KEY environment variable.")
        return False
    
    # Initialize ThingSpeak API
    api = ThingSpeakAPI(api_key)
    
    # Test connection
    return api.test_connection()

if __name__ == "__main__":
    try:
        success = test_thingspeak()
        if success:
            print("\nThingSpeak connection test passed!")
            exit(0)
        else:
            print("\nThingSpeak connection test failed!")
            exit(1)
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
        exit(1)
    except Exception as e:
        print(f"\nUnexpected error during test: {str(e)}")
        exit(1) 