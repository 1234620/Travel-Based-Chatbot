import os
import httpx
from fastapi import HTTPException
from dotenv import load_dotenv
import logging

load_dotenv()
logging.basicConfig(level=logging.INFO)

AMADEUS_API_KEY = os.getenv("AMADEUS_API_KEY")
AMADEUS_API_SECRET = os.getenv("AMADEUS_API_SECRET")

class HotelAgent:
    def __init__(self):
        self.api_key = AMADEUS_API_KEY
        self.api_secret = AMADEUS_API_SECRET
        self.base_url = "https://test.api.amadeus.com/v1"
        self.access_token = None

        if not self.api_key or not self.api_secret:
            logging.warning("HotelAgent initialized with missing Amadeus API key!")
        else:
            self._get_access_token()

    def _get_access_token(self):
        """Get OAuth2 access token from Amadeus"""
        try:
            url = "https://test.api.amadeus.com/v1/security/oauth2/token"
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            data = {
                "grant_type": "client_credentials",
                "client_id": self.api_key,
                "client_secret": self.api_secret
            }
            
            with httpx.Client() as client:
                response = client.post(url, headers=headers, data=data)
                response.raise_for_status()
                token_data = response.json()
                self.access_token = token_data.get("access_token")
                logging.info("Successfully obtained Amadeus access token")
        except Exception as e:
            logging.error(f"Failed to get Amadeus access token: {e}")
            self.access_token = None

    async def search_hotels(self, latitude: float, longitude: float, checkin: str, checkout: str, adults: int = 2, radius: int = 50):
        """Search for hotels using Amadeus Hotel List API"""
        if not self.access_token:
            logging.warning("No access token available, attempting to get one")
            self._get_access_token()
            if not self.access_token:
                raise HTTPException(status_code=500, detail="Failed to authenticate with Amadeus API")

        try:
            url = f"{self.base_url}/reference-data/locations/hotels/by-geocode"
            headers = {"Authorization": f"Bearer {self.access_token}"}
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "radius": radius,
                "radiusUnit": "KM",
                "hotelSource": "ALL"
            }

            logging.info(f"Searching hotels at lat={latitude}, lng={longitude}, radius={radius}km")

            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=headers, params=params, timeout=10.0)
                response.raise_for_status()
                hotels_data = response.json()

                if not hotels_data.get("data"):
                    logging.warning("No hotels found in the area")
                    return {"data": [], "meta": {}}

                logging.info(f"Found {len(hotels_data.get('data', []))} hotels")
                return hotels_data

        except httpx.HTTPStatusError as e:
            logging.error(f"Amadeus API error: {e.response.status_code} - {e.response.text}")
            raise HTTPException(status_code=e.response.status_code, detail=f"Amadeus API error: {e.response.text}")
        except Exception as e:
            logging.error(f"Hotel search error: {e}")
            raise HTTPException(status_code=500, detail=f"Hotel search failed: {str(e)}")
