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
        # Amadeus Hotels API endpoints
        self.token_url = "https://test.api.amadeus.com/v1/security/oauth2/token"
        self.search_url = "https://test.api.amadeus.com/v1/reference-data/locations/hotels/by-geocode"
        self.offers_url = "https://test.api.amadeus.com/v3/shopping/hotel-offers"
        self.api_key = AMADEUS_API_KEY
        self.api_secret = AMADEUS_API_SECRET
        self.access_token = None
        
        # Safe logging of API key
        if self.api_key:
            logging.info(f"HotelAgent initialized with Amadeus API key: {self.api_key[:5]}...")
        else:
            logging.warning("HotelAgent initialized with missing Amadeus API key!")

    async def authenticate(self):
        """Authenticate with Amadeus API"""
        if not self.api_key or not self.api_secret:
            error_msg = "Missing Amadeus API credentials. Check your .env file."
            logging.error(error_msg)
            return {"error": error_msg}
            
        data = (
            f"grant_type=client_credentials&client_id={self.api_key}&client_secret={self.api_secret}"
        )
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        try:
            logging.info(f"Authenticating with Amadeus API for hotels")
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.post(self.token_url, data=data, headers=headers)
                logging.info(f"Amadeus auth response: {response.status_code}")
                
                if response.status_code == 200:
                    token_data = response.json()
                    self.access_token = token_data["access_token"]
                    logging.info(f"Authentication successful, token received")
                    return token_data
                else:
                    error_msg = f"Amadeus authentication failed: {response.text}"
                    logging.error(error_msg)
                    return {"error": error_msg}
        except Exception as e:
            error_msg = f"Amadeus authentication error: {str(e)}"
            logging.error(error_msg)
            return {"error": error_msg}

    async def search_hotels(self, latitude, longitude, checkin, checkout, adults=2, radius=50):
        """Search hotels using Amadeus API"""
        try:
            if not self.access_token:
                logging.info("No access token found, authenticating first")
                auth_result = await self.authenticate()
                if "error" in auth_result:
                    return {"data": [], "error": auth_result["error"]}
                
            logging.info(f"Searching hotels near lat={latitude}, lng={longitude} from {checkin} to {checkout}")
            headers = {"Authorization": f"Bearer {self.access_token}"}
            
            # First, get hotels by geocode
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "radius": radius,
                "radiusUnit": "KM"
            }
            
            async with httpx.AsyncClient(timeout=30) as client:
                # Step 1: Get hotel IDs by location
                logging.info(f"Getting hotels by geocode: {params}")
                response = await client.get(self.search_url, headers=headers, params=params)
                logging.info(f"Amadeus geocode response: {response.status_code}")
                
                if response.status_code != 200:
                    if response.status_code == 401:
                        # Token expired, re-authenticate
                        logging.info("Token expired, re-authenticating")
                        auth_result = await self.authenticate()
                        if "error" in auth_result:
                            return {"data": [], "error": auth_result["error"]}
                        headers = {"Authorization": f"Bearer {self.access_token}"}
                        response = await client.get(self.search_url, headers=headers, params=params)
                    
                    if response.status_code != 200:
                        error_msg = f"Hotel geocode search failed: {response.text}"
                        logging.error(error_msg)
                        return {"data": [], "error": error_msg}
                
                geocode_result = response.json()
                hotel_ids = [hotel["hotelId"] for hotel in geocode_result.get("data", [])[:10]]  # Limit to 10 hotels
                
                if not hotel_ids:
                    logging.info("No hotels found in the specified area")
                    return {"data": [], "message": "No hotels found in the specified area"}
                
                logging.info(f"Found {len(hotel_ids)} hotels: {hotel_ids}")
                
                # Step 2: Get hotel offers
                offers_params = {
                    "hotelIds": ",".join(hotel_ids),
                    "checkInDate": checkin,
                    "checkOutDate": checkout,
                    "adults": adults,
                    "currency": "INR"  # Use INR for Indian market
                }
                
                logging.info(f"Getting hotel offers: {offers_params}")
                response = await client.get(self.offers_url, headers=headers, params=offers_params)
                logging.info(f"Amadeus offers response: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    hotel_count = len(result.get("data", []))
                    logging.info(f"Found {hotel_count} hotels with offers")
                    return result
                else:
                    error_msg = f"Hotel offers search failed: {response.text}"
                    logging.error(error_msg)
                    return {"data": [], "error": error_msg}
                    
        except Exception as e:
            error_msg = f"Hotel search exception: {str(e)}"
            logging.error(error_msg)
            return {"data": [], "error": error_msg}
