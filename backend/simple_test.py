import requests
import time

print("Testing backend connection...")

# Wait a bit for server to start
time.sleep(2)

try:
    # Test basic health check
    response = requests.get("http://localhost:8000/", timeout=5)
    print(f"✅ Server is running! Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    # Test the flight API
    print("\nTesting flight API...")
    response = requests.post(
        "http://localhost:8000/api/search-flights",
        json={
            "origin": "DEL",
            "destination": "BOM", 
            "departure_date": "2025-10-21",
            "adults": 1
        },
        timeout=10
    )
    
    print(f"Flight API Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ SUCCESS! Found {len(data.get('outbound_flights', []))} flights")
    else:
        print(f"❌ ERROR: {response.text}")
        
except requests.exceptions.ConnectionError:
    print("❌ CONNECTION ERROR: Server is not running on port 8000")
except requests.exceptions.Timeout:
    print("❌ TIMEOUT ERROR: Server took too long to respond")
except Exception as e:
    print(f"❌ ERROR: {e}")
