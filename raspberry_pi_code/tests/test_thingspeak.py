#!/usr/bin/env python3

from raspberry_pi_code.config import THINGSPEAK_API_KEY
from raspberry_pi_code.services.api.thingspeak import ThingSpeakAPI

def test_thingspeak():
    print("\nTesting ThingSpeak Connection:")
    print("-" * 30)
    
    # Initialize ThingSpeak API with key from config
    api = ThingSpeakAPI(THINGSPEAK_API_KEY)
    
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