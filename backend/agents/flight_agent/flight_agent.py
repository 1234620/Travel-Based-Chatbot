import os
import httpx
from fastapi import HTTPException
from dotenv import load_dotenv
import logging
import json

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
        
        # Safe logging of API key (check if it exists first)
        if self.api_key:
            logging.info(f"FlightAgent initialized with API key: {self.api_key[:5]}...")
        else:
            logging.warning("FlightAgent initialized with missing API key!")

    async def authenticate(self):
        if not self.api_key or not self.api_secret:
            error_msg = "Missing Amadeus API credentials. Check your .env file."
            logging.error(error_msg)
            return {"error": error_msg}
            
        data = (
            f"grant_type=client_credentials&client_id={self.api_key}&client_secret={self.api_secret}"
        )
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        try:
            logging.info(f"Authenticating with Amadeus API")
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

    async def search_flights(self, origin, destination, departure_date, return_date=None, adults=1, children=0, infants=0):
        try:
            if not self.access_token:
                logging.info("No access token found, authenticating first")
                auth_result = await self.authenticate()
                if "error" in auth_result:
                    return {"data": [], "error": auth_result["error"]}
                
            logging.info(f"Searching flights from {origin} to {destination} on {departure_date}")
            headers = {"Authorization": f"Bearer {self.access_token}"}
            params = {
                "originLocationCode": origin,
                "destinationLocationCode": destination,
                "departureDate": departure_date,
                "adults": adults,
                "max": 10,  # Limit results for faster response
                "currencyCode": "INR"  # Return prices in Indian Rupees
            }
            
            # Note: Amadeus API doesn't support return_date in single call
            # Round-trip searches should be handled with separate outbound and return calls
            
            # Add children and infants if provided
            if children > 0:
                params["children"] = children
            if infants > 0:
                params["infants"] = infants
            
            async with httpx.AsyncClient(timeout=30) as client:
                logging.info(f"Making request to {self.search_url} with params: {params}")
                response = await client.get(self.search_url, headers=headers, params=params)
                logging.info(f"Amadeus flight search response: {response.status_code}")
                
                if response.status_code == 200:
                    result = response.json()
                    flight_count = len(result.get("data", []))
                    logging.info(f"Found {flight_count} flights")
                    return result
                elif response.status_code == 401:
                    # Token expired, try to re-authenticate
                    logging.info("Token expired, re-authenticating")
                    auth_result = await self.authenticate()
                    if "error" in auth_result:
                        return {"data": [], "error": auth_result["error"]}
                        
                    # Retry the request with new token
                    headers = {"Authorization": f"Bearer {self.access_token}"}
                    response = await client.get(self.search_url, headers=headers, params=params)
                    
                    if response.status_code == 200:
                        result = response.json()
                        flight_count = len(result.get("data", []))
                        logging.info(f"Found {flight_count} flights after re-authentication")
                        return result
                    else:
                        error_msg = f"Flight search failed after re-auth: {response.text}"
                        logging.error(error_msg)
                        return {"data": [], "error": error_msg}
                else:
                    error_msg = f"Flight search failed: {response.text}"
                    logging.error(error_msg)
                    return {"data": [], "error": error_msg}
        except Exception as e:
            error_msg = f"Flight search exception: {str(e)}"
            logging.error(error_msg)
            return {"data": [], "error": error_msg}
