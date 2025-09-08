import os
import httpx
from fastapi import HTTPException
from dotenv import load_dotenv
import logging

load_dotenv()
logging.basicConfig(level=logging.INFO)

AMADEUS_API_KEY = os.getenv("AMADEUS_API_KEY")
AMADEUS_API_SECRET = os.getenv("AMADEUS_API_SECRET")

class FlightAgent:
    def __init__(self):
        self.token_url = "https://test.api.amadeus.com/v1/security/oauth2/token"
        self.search_url = "https://test.api.amadeus.com/v2/shopping/flight-offers"
        self.api_key = AMADEUS_API_KEY
        self.api_secret = AMADEUS_API_SECRET
        self.access_token = None

    async def authenticate(self):
        data = (
            f"grant_type=client_credentials&client_id={self.api_key}&client_secret={self.api_secret}"
        )
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.post(self.token_url, data=data, headers=headers)
                logging.info(f"Amadeus auth response: {response.status_code} {response.text}")
                if response.status_code == 200:
                    self.access_token = response.json()["access_token"]
                else:
                    raise HTTPException(status_code=500, detail=f"Amadeus authentication failed: {response.text}")
        except Exception as e:
            logging.error(f"Amadeus authentication error: {e}")
            raise HTTPException(status_code=500, detail=f"Amadeus authentication exception: {str(e)}")

    async def search_flights(self, origin, destination, departure_date):
        if not self.access_token:
            await self.authenticate()
        headers = {"Authorization": f"Bearer {self.access_token}"}
        params = {
            "originLocationCode": origin,
            "destinationLocationCode": destination,
            "departureDate": departure_date,
            "adults": 1
        }
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                response = await client.get(self.search_url, headers=headers, params=params)
                logging.info(f"Amadeus flight search response: {response.status_code} {response.text}")
                if response.status_code == 200:
                    return response.json()
                else:
                    raise HTTPException(status_code=response.status_code, detail=f"Flight search failed: {response.text}")
        except Exception as e:
            logging.error(f"Flight search error: {e}")
            raise HTTPException(status_code=500, detail=f"Flight search exception: {str(e)}")
