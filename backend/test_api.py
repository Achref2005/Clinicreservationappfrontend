"""
Simple test script for the Clinic Reservation API
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}\n")

def test_chat():
    """Test chat endpoint"""
    print("Testing chat endpoint...")
    
    # Create session
    response = requests.post(f"{BASE_URL}/api/chat/session/new")
    session_id = response.json()["session_id"]
    print(f"Session ID: {session_id}\n")
    
    # Send messages
    messages = [
        "My name is John Smith",
        "My phone number is 5551234567",
        "I want an appointment tomorrow at 2 PM"
    ]
    
    for message in messages:
        print(f"Sending: {message}")
        response = requests.post(
            f"{BASE_URL}/api/chat/",
            json={"message": message, "session_id": session_id}
        )
        data = response.json()
        print(f"Response: {data['message']}\n")

def test_appointments():
    """Test appointments endpoint"""
    print("Testing appointments endpoint...")
    response = requests.get(f"{BASE_URL}/api/appointments/")
    appointments = response.json()
    print(f"Found {len(appointments)} appointments\n")
    for apt in appointments[:3]:  # Show first 3
        print(f"  - {apt['patient_name']}: {apt['appointment_date']} at {apt['appointment_time']}")

def test_availability():
    """Test availability check"""
    print("Testing availability check...")
    from datetime import datetime, timedelta
    tomorrow = datetime.now() + timedelta(days=1)
    date_str = tomorrow.isoformat()
    
    response = requests.get(
        f"{BASE_URL}/api/appointments/availability/check",
        params={"date": date_str, "time": "14:00"}
    )
    data = response.json()
    print(f"Available: {data['available']}\n")

if __name__ == "__main__":
    print("=" * 50)
    print("Clinic Reservation API Test")
    print("=" * 50)
    print()
    
    try:
        test_health()
        test_chat()
        test_appointments()
        test_availability()
        print("=" * 50)
        print("✅ All tests completed!")
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to API. Make sure the backend is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")





