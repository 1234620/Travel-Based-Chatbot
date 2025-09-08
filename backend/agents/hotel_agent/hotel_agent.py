import os
import httpx
from fastapi import HTTPException
from dotenv import load_dotenv
import logging

load_dotenv()
logging.basicConfig(level=logging.INFO)

BOOKING_API_KEY = os.getenv("BOOKING_API_KEY")  # Add this to your .env if using RapidAPI

class HotelAgent:
    def __init__(self):
        # Correct RapidAPI endpoint for Booking.com hotel search
        self.search_url = "https://booking-com15.p.rapidapi.com/api/v1/hotels/searchHotels"
        self.api_key = BOOKING_API_KEY

    # Removed duplicate/old method signature
    async def search_hotels(self, dest_id, search_type, arrival_date, departure_date, adults=1, children_age="0,17", room_qty=1, page_number=1, price_min=0, price_max=0, sort_by=None, categories_filter=None, units="metric", temperature_unit="c", languagecode="en-us", currency_code="AED", location="US"):
        headers = {
            "X-RapidAPI-Key": self.api_key,
            "X-RapidAPI-Host": "booking-com15.p.rapidapi.com"
        }
        params = {
            "dest_id": dest_id,
            "search_type": search_type,
            "arrival_date": arrival_date,
            "departure_date": departure_date,
            "adults": adults,
            "children_age": children_age,
            "room_qty": room_qty,
            "page_number": page_number,
            "price_min": price_min,
            "price_max": price_max,
            "sort_by": sort_by,
            "categories_filter": categories_filter,
            "units": units,
            "temperature_unit": temperature_unit,
            "languagecode": languagecode,
            "currency_code": currency_code,
            "location": location
        }
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                response = await client.get(self.search_url, headers=headers, params=params)
                logging.info(f"Booking.com hotel search response: {response.status_code} {response.text}")
                if response.status_code == 200:
                    return response.json()
                else:
                    raise HTTPException(status_code=response.status_code, detail=f"Hotel search failed: {response.text}")
        except Exception as e:
            logging.error(f"Hotel search error: {e}")
            raise HTTPException(status_code=500, detail=f"Hotel search exception: {str(e)}")
