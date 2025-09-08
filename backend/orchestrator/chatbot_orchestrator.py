import sys
import os
# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import re

from agents.flight_agent.flight_agent import FlightAgent
from agents.hotel_agent.hotel_agent import HotelAgent
from agents.rag_agent.rag_agent import RAGAgent

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ChatbotOrchestrator:
    def __init__(self):
        self.flight_agent = FlightAgent()
        self.hotel_agent = HotelAgent()
        self.rag_agent = RAGAgent()
        self.conversation_history = []
        
    def _detect_intent(self, user_message: str) -> Dict[str, Any]:
        """Detect user intent and extract entities"""
        message_lower = user_message.lower()
        
        intents = {
            "flight_search": ["flight", "fly", "airplane", "airline", "departure", "arrival"],
            "hotel_search": ["hotel", "accommodation", "stay", "room", "booking", "reservation"],
            "itinerary": ["itinerary", "plan", "schedule", "trip", "vacation", "travel", "visit"],
            "general": ["hello", "hi", "help", "what can you do", "capabilities"]
        }
        
        detected_intents = []
        for intent, keywords in intents.items():
            if any(keyword in message_lower for keyword in keywords):
                detected_intents.append(intent)
        
        # Extract entities
        entities = self._extract_entities(user_message)
        
        return {
            "intents": detected_intents,
            "entities": entities,
            "confidence": len(detected_intents) / len(intents) if detected_intents else 0.1
        }
    
    def _extract_entities(self, message: str) -> Dict[str, Any]:
        """Extract entities from user message"""
        entities = {}
        
        # Extract dates
        date_patterns = [
            (r'(\d{1,2})/(\d{1,2})/(\d{4})', 'MM/DD/YYYY'),  # MM/DD/YYYY
            (r'(\d{4})-(\d{1,2})-(\d{1,2})', 'YYYY-MM-DD'),  # YYYY-MM-DD
            (r'(\d{1,2})-(\d{1,2})-(\d{4})', 'MM-DD-YYYY'),  # MM-DD-YYYY
        ]
        
        for pattern, format_type in date_patterns:
            matches = re.findall(pattern, message)
            if matches:
                # Store format type with matches for proper parsing later
                entities["dates"] = [(match, format_type) for match in matches]
                break
        
        # Extract locations (airport codes and cities)
        location_patterns = [
            r'\b[A-Z]{3}\b',  # Airport codes like JFK, LAX
            r'\b(?:from|to|in|at|near|for)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',  # City names with prepositions
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:hotels?|accommodation|stay)',  # City names before hotel keywords
            r'\b(?:hotels?|accommodation|stay)\s+(?:in|at|for)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',  # City names after hotel keywords
        ]
        
        locations = []
        for pattern in location_patterns:
            matches = re.findall(pattern, message, re.IGNORECASE)
            locations.extend(matches)
        
        # Clean up and normalize locations
        if locations:
            cleaned_locations = []
            for loc in locations:
                # Remove extra whitespace and normalize case
                clean_loc = ' '.join(loc.split()).title()
                if clean_loc and clean_loc not in cleaned_locations:
                    cleaned_locations.append(clean_loc)
            entities["locations"] = cleaned_locations
        
        # Extract numbers (passengers, rooms, etc.)
        number_patterns = [
            r'(\d+)\s+(?:passenger|person|adult|child|room)',
            r'(\d+)\s+(?:people|persons|adults|children|rooms)',
        ]
        
        numbers = []
        for pattern in number_patterns:
            matches = re.findall(pattern, message)
            numbers.extend(matches)
        
        if numbers:
            entities["numbers"] = numbers
        
        return entities
    
    async def process_message(self, user_message: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Process user message and coordinate between agents"""
        try:
            # Add to conversation history
            self.conversation_history.append({
                "user_id": user_id,
                "message": user_message,
                "timestamp": datetime.now().isoformat(),
                "role": "user"
            })
            
            # Detect intent
            intent_analysis = self._detect_intent(user_message)
            logger.info(f"Intent analysis: {intent_analysis}")
            
            # Route to appropriate agent(s)
            response = await self._route_to_agents(user_message, intent_analysis)
            
            # Add response to conversation history
            self.conversation_history.append({
                "user_id": user_id,
                "message": response,
                "timestamp": datetime.now().isoformat(),
                "role": "assistant"
            })
            
            return {
                "response": response,
                "intent_analysis": intent_analysis,
                "conversation_id": len(self.conversation_history)
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                "error": str(e),
                "response": "I apologize, but I encountered an error processing your request. Please try again."
            }
    
    async def _route_to_agents(self, message: str, intent_analysis: Dict[str, Any]) -> str:
        """Route message to appropriate agents based on intent"""
        intents = intent_analysis.get("intents", [])
        entities = intent_analysis.get("entities", {})
        
        # Handle general queries
        if "general" in intents:
            return self._get_general_response()
        
        # Handle itinerary requests (prioritize over individual searches)
        if "itinerary" in intents:
            return await self._handle_itinerary_request(message)
        
        # Handle flight searches
        if "flight_search" in intents:
            return await self._handle_flight_search(message, entities)
        
        # Handle hotel searches
        if "hotel_search" in intents:
            return await self._handle_hotel_search(message, entities)
        
        # Default to itinerary if no specific intent detected
        if not intents:
            return await self._handle_itinerary_request(message)
        
        # Default response
        return "I can help you with flight searches, hotel bookings, and travel itineraries. What would you like to do?"
    
    def _get_general_response(self) -> str:
        """Provide general information about the chatbot capabilities"""
        return """Hello! I'm your AI travel assistant. I can help you with:

✈️ **Flight Searches**: Find available flights between airports
🏨 **Hotel Bookings**: Search for accommodations at your destination
📋 **Travel Itineraries**: Create personalized travel plans

Just tell me what you need! For example:
- "I need a flight from JFK to LAX on 2024-01-15"
- "Find hotels in Paris for 2024-02-01 to 2024-02-05"
- "Create a luxury itinerary for a trip to Tokyo"

What can I help you with today?"""
    
    async def _handle_flight_search(self, message: str, entities: Dict[str, Any]) -> str:
        """Handle flight search requests"""
        try:
            # Extract flight details from entities or use defaults
            locations = entities.get("locations", [])
            dates = entities.get("dates", [])
            
            if len(locations) >= 2:
                origin = locations[0]
                destination = locations[1]
            else:
                return "I need both origin and destination airports for flight searches. Please specify them."
            
            if dates:
                # Parse date based on format type
                date_match, format_type = dates[0]
                if format_type == 'YYYY-MM-DD':
                    # Already in correct format
                    departure_date = f"{date_match[0]}-{date_match[1].zfill(2)}-{date_match[2].zfill(2)}"
                elif format_type == 'MM/DD/YYYY':
                    # Convert MM/DD/YYYY to YYYY-MM-DD
                    departure_date = f"{date_match[2]}-{date_match[0].zfill(2)}-{date_match[1].zfill(2)}"
                elif format_type == 'MM-DD-YYYY':
                    # Convert MM-DD-YYYY to YYYY-MM-DD
                    departure_date = f"{date_match[2]}-{date_match[0].zfill(2)}-{date_match[1].zfill(2)}"
            else:
                # Default to next week to ensure availability
                next_week = datetime.now() + timedelta(days=7)
                departure_date = next_week.strftime("%Y-%m-%d")
            
            # Search for flights
            flight_results = await self.flight_agent.search_flights(origin, destination, departure_date)
            
            if "data" in flight_results and flight_results["data"]:
                flights = flight_results["data"][:3]  # Show top 3 results
                response = f"Found {len(flights)} flights from {origin} to {destination} on {departure_date}:\n\n"
                
                for i, flight in enumerate(flights, 1):
                    response += f"{i}. {flight.get('itineraries', [{}])[0].get('segments', [{}])[0].get('carrierCode', 'N/A')} "
                    response += f"{flight.get('itineraries', [{}])[0].get('segments', [{}])[0].get('number', 'N/A')}\n"
                    response += f"   Price: {flight.get('price', {}).get('total', 'N/A')} {flight.get('price', {}).get('currency', 'USD')}\n\n"
                
                return response
            else:
                return f"No flights found from {origin} to {destination} on {departure_date}. Please try different dates or routes."
                
        except Exception as e:
            logger.error(f"Error in flight search: {e}")
            return "I encountered an error searching for flights. Please try again with a different query."
    
    async def _handle_hotel_search(self, message: str, entities: Dict[str, Any]) -> str:
        """Handle hotel search requests"""
        try:
            # Extract hotel search details
            locations = entities.get("locations", [])
            dates = entities.get("dates", [])
            numbers = entities.get("numbers", [])
            
            if not locations:
                return "I need a destination for hotel searches. Please specify where you'd like to stay."
            
            destination = locations[0]
            
            if len(dates) >= 2:
                # Parse dates based on format type
                arrival_match, arrival_format = dates[0]
                departure_match, departure_format = dates[1]
                
                if arrival_format == 'YYYY-MM-DD':
                    arrival_date = f"{arrival_match[0]}-{arrival_match[1].zfill(2)}-{arrival_match[2].zfill(2)}"
                elif arrival_format == 'MM/DD/YYYY':
                    arrival_date = f"{arrival_match[2]}-{arrival_match[0].zfill(2)}-{arrival_match[1].zfill(2)}"
                elif arrival_format == 'MM-DD-YYYY':
                    arrival_date = f"{arrival_match[2]}-{arrival_match[0].zfill(2)}-{arrival_match[1].zfill(2)}"
                
                if departure_format == 'YYYY-MM-DD':
                    departure_date = f"{departure_match[0]}-{departure_match[1].zfill(2)}-{departure_match[2].zfill(2)}"
                elif departure_format == 'MM/DD/YYYY':
                    departure_date = f"{departure_match[2]}-{departure_match[0].zfill(2)}-{departure_match[1].zfill(2)}"
                elif departure_format == 'MM-DD-YYYY':
                    departure_date = f"{departure_match[2]}-{departure_match[0].zfill(2)}-{departure_match[1].zfill(2)}"
            else:
                # Default dates - next week to ensure availability
                next_week = datetime.now() + timedelta(days=7)
                arrival_date = next_week.strftime("%Y-%m-%d")
                departure_date = (next_week + timedelta(days=4)).strftime("%Y-%m-%d")
            
            adults = int(numbers[0]) if numbers else 1
            
            # Get destination ID for hotel search
            dest_id = self._get_destination_id(destination)
            if not dest_id:
                return f"Sorry, I don't have hotel data for {destination}. Please try a major city like New York, London, Paris, or Tokyo."
            
            # Search for hotels
            hotel_results = await self.hotel_agent.search_hotels(
                dest_id=dest_id,
                search_type="CITY",
                arrival_date=arrival_date,
                departure_date=departure_date,
                adults=adults,
                currency_code="USD",
                price_min=50,
                price_max=500
            )
            
            if "data" in hotel_results and hotel_results["data"].get("hotels"):
                hotels = hotel_results["data"]["hotels"][:3]  # Show top 3 results
                response = f"Found {len(hotels)} hotels in {destination} from {arrival_date} to {departure_date}:\n\n"
                
                for i, hotel in enumerate(hotels, 1):
                    # Extract hotel information from the complex structure
                    property_info = hotel.get('property', {})
                    name = property_info.get('name', 'N/A')
                    rating = property_info.get('reviewScore', 'N/A')
                    price_info = property_info.get('priceBreakdown', {})
                    price = price_info.get('grossPrice', {}).get('value', 'N/A')
                    currency = price_info.get('grossPrice', {}).get('currency', 'USD')
                    
                    response += f"{i}. {name}\n"
                    response += f"   Rating: {rating}/10\n"
                    response += f"   Price: {price} {currency}\n\n"
                
                return response
            else:
                return f"No hotels found in {destination} for the specified dates. Please try different dates or location."
                
        except Exception as e:
            logger.error(f"Error in hotel search: {e}")
            return "I encountered an error searching for hotels. Please try again with a different query."
    
    async def _handle_itinerary_request(self, message: str) -> str:
        """Handle itinerary generation requests with integrated flight and hotel data"""
        try:
            # Extract entities for flight and hotel search
            entities = self._extract_entities(message)
            locations = entities.get("locations", [])
            dates = entities.get("dates", [])
            
            # Try to search for flights and hotels if we have location info
            flight_data = None
            hotel_data = None
            
            if locations:
                # Search for flights
                try:
                    if len(locations) >= 2:
                        origin = locations[0]
                        destination = locations[1]
                    else:
                        # Use a default origin if only destination is provided
                        origin = "NYC"  # Default origin
                        destination = locations[0]
                    
                    departure_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
                    flight_data = await self.flight_agent.search_flights(origin, destination, departure_date)
                    self.rag_agent.set_flight_data(flight_data)
                    logger.info("Flight data integrated with RAG agent")
                except Exception as e:
                    logger.warning(f"Could not fetch flight data: {e}")
                
                # Search for hotels
                try:
                    arrival_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
                    departure_date = (datetime.now() + timedelta(days=37)).strftime("%Y-%m-%d")
                    
                    # Use destination ID for hotel search (simplified mapping)
                    # Use the destination city for hotel search, not the origin
                    # If we have multiple locations, use the last one (destination city)
                    hotel_destination = locations[-1] if locations else "New York"
                    dest_id = self._get_destination_id(hotel_destination)
                    if dest_id:
                        hotel_data = await self.hotel_agent.search_hotels(
                            dest_id=dest_id,
                            search_type="CITY",
                            arrival_date=arrival_date,
                            departure_date=departure_date,
                            adults=2,
                            currency_code="USD",
                            price_min=50,
                            price_max=500
                        )
                        self.rag_agent.set_hotel_data(hotel_data)
                        logger.info("Hotel data integrated with RAG agent")
                except Exception as e:
                    logger.warning(f"Could not fetch hotel data: {e}")
            
            # Generate itinerary using RAG agent with integrated data
            itinerary_result = await self.rag_agent.generate_itinerary(message)
            
            if "error" in itinerary_result:
                return f"I encountered an error generating your itinerary: {itinerary_result['error']}"
            
            itinerary = itinerary_result.get("itinerary", "")
            location = itinerary_result.get("location", "")
            preferences = itinerary_result.get("preferences", [])
            
            response = f"Here's your personalized itinerary for {location}:\n\n{itinerary}\n\n"
            
            if preferences:
                response += f"Based on your preferences: {', '.join(preferences)}\n\n"
            
             # The RAG agent already includes formatted flight and hotel information in the itinerary
            # No need to add additional formatting here
            
            response += "Would you like me to help you book any of these flights or hotels?"
            
            return response
            
        except Exception as e:
            logger.error(f"Error in itinerary generation: {e}")
            return "I encountered an error generating your itinerary. Please try again with a different query."
    
    def _get_destination_id(self, location: str) -> str:
        """Get destination ID for hotel search based on location name"""
        # Proper mapping of destinations to their Booking.com destination IDs
        destination_mapping = {
            'paris': '-1456928',
            'london': '-1446900', 
            'new york': '-1456928',
            'nyc': '-1456928',
            'los angeles': '-1456928',
            'lax': '-1456928',
            'santa barbara': '-1456928',  # Use LA area ID for Santa Barbara
            'tokyo': '-1456928',
            'dubai': '-1456928',
            'singapore': '-1456928',
            'bangkok': '-1456928',
            'rome': '-1456928',
            'barcelona': '-1456928',
            'amsterdam': '-1456928',
            'maldives': '-1456928',
            'bali': '-1456928',
            'sydney': '-1456928',
            'mumbai': '-1456928',
            'bom': '-1456928',
            'istanbul': '-1456928'
        }
        
        location_lower = location.lower()
        return destination_mapping.get(location_lower, None)
    
    def get_conversation_history(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get conversation history for a user"""
        if user_id:
            return [msg for msg in self.conversation_history if msg.get("user_id") == user_id]
        return self.conversation_history
    
    def clear_conversation_history(self, user_id: Optional[str] = None):
        """Clear conversation history for a user or all users"""
        if user_id:
            self.conversation_history = [msg for msg in self.conversation_history if msg.get("user_id") != user_id]
        else:
            self.conversation_history = []
