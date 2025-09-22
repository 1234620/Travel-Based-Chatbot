import asyncio
import httpx
import json

async def test_frontend_api():
    """Test the new frontend API endpoint"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/api/search-flights",
                json={
                    "origin": "DEL",
                    "destination": "BOM", 
                    "departure_date": "2025-10-21",
                    "adults": 1
                }
            )
            
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success") and data.get("outbound_flights"):
                    print(f"✅ API Test SUCCESS - Found {len(data['outbound_flights'])} flights")
                else:
                    print("❌ API Test FAILED - No flights found")
            else:
                print(f"❌ API Test FAILED - Status {response.status_code}")
                
    except Exception as e:
        print(f"❌ API Test ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(test_frontend_api())

