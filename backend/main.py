import sys
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from .env file (project root)
# Get the project root directory (parent of backend)
project_root = Path(__file__).parent.parent
env_path = project_root / '.env'

print(f"Loading .env from: {env_path}")
print(f".env exists: {env_path.exists()}")

load_dotenv(dotenv_path=env_path)

# Verify environment variables are loaded
print(f"GEMINI_API_KEY loaded: {os.getenv('GEMINI_API_KEY') is not None}")

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from agents.flight_agent.flight_agent import FlightAgent
from agents.hotel_agent.hotel_agent import HotelAgent
from agents.rag_agent.rag_agent import RAGAgent
from orchestrator.chatbot_orchestrator import ChatbotOrchestrator
import asyncio
import json
import logging
from datetime import datetime, timedelta
import re

app = FastAPI(title="NLP Multi-Agent Travel Chatbot", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the orchestrator
orchestrator = ChatbotOrchestrator()

# Initialize RAG agent for chat endpoint
rag_agent = None
try:
    rag_agent = RAGAgent()
    logging.info("RAG agent initialized successfully")
except Exception as e:
    logging.error(f"Failed to initialize RAG agent: {e}")

# Pydantic models for request/response
class ChatMessage(BaseModel):
    message: str
    user_id: str = None

class ChatRequest(BaseModel):
    message: str
    
class ChatResponse(BaseModel):
    response: str
    intent_analysis: dict = None
    conversation_id: int = None
    error: str = None

@app.get("/")
def read_root():
    return {"message": "NLP Multi-Agent Travel Chatbot Backend is running."}

# Placeholder endpoints for agents
@app.get("/flight")
async def flight_agent(
    origin: str = Query(..., description="Origin airport code"),
    destination: str = Query(..., description="Destination airport code"),
    departure_date: str = Query(..., description="Departure date in YYYY-MM-DD format")
):
    agent = FlightAgent()
    result = await agent.search_flights(origin, destination, departure_date)
    return result

@app.get("/hotel")
async def hotel_agent(
    latitude: float = Query(..., description="Latitude for hotel search (e.g., 19.0760 for Mumbai)"),
    longitude: float = Query(..., description="Longitude for hotel search (e.g., 72.8777 for Mumbai)"),
    checkin: str = Query(..., description="Check-in date in YYYY-MM-DD format"),
    checkout: str = Query(..., description="Check-out date in YYYY-MM-DD format"),
    adults: int = Query(2, description="Number of adults"),
    radius: int = Query(50, description="Search radius in kilometers")
):
    try:
        agent = HotelAgent()
        result = await agent.search_hotels(
            latitude=latitude,
            longitude=longitude,
            checkin=checkin,
            checkout=checkout,
            adults=adults,
            radius=radius
        )
        return result
    except Exception as e:
        logging.error(f"Hotel agent error: {e}")
        raise HTTPException(status_code=500, detail=f"Hotel search failed: {str(e)}")

@app.get("/rag")
async def rag_agent(
    query: str = Query(..., description="Travel query for itinerary generation"),
    include_flights: bool = Query(False, description="Include flight data in itinerary"),
    include_hotels: bool = Query(False, description="Include hotel data in itinerary")
):
    """
    Generate a travel itinerary using RAG agent
    Example: /rag?query=Plan a 5-day luxury trip to Tokyo&include_flights=true&include_hotels=true
    """
    try:
        agent = RAGAgent()
        
        # Check if initialization failed
        if agent.initialization_error:
            raise HTTPException(
                status_code=500,
                detail=f"RAG agent initialization failed: {agent.initialization_error}"
            )
        
        # Generate itinerary
        result = await agent.generate_itinerary(query)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        # Preprocess the itinerary markdown for better formatting
        if "itinerary" in result:
            result["itinerary"] = preprocess_markdown(result["itinerary"])
        
        return {
            "success": True,
            "query": query,
            "itinerary": result.get("itinerary"),
            "location": result.get("location"),
            "preferences": result.get("preferences"),
            "sources": result.get("sources", []),
            "flight_data": result.get("flight_data") if include_flights else None,
            "hotel_data": result.get("hotel_data") if include_hotels else None
        }
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"RAG endpoint error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"RAG agent exception: {str(e)}")

@app.get("/rag/integrated")
async def integrated_itinerary(
    query: str = Query(..., description="Travel query"),
    origin: str = Query("NYC", description="Origin airport code"),
    destination: str = Query(None, description="Destination airport code"),
    departure_date: str = Query(None, description="Departure date in YYYY-MM-DD format"),
    arrival_date: str = Query(None, description="Arrival date in YYYY-MM-DD format"),
    departure_date_hotel: str = Query(None, description="Hotel departure date in YYYY-MM-DD format")
):
    """Generate integrated itinerary with flight and hotel data"""
    try:
        # Initialize agents
        flight_agent = FlightAgent()
        hotel_agent = HotelAgent()
        rag_agent = RAGAgent()
        
        # Set default dates if not provided
        if not departure_date:
            departure_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        if not arrival_date:
            arrival_date = (datetime.now() + timedelta(days=37)).strftime("%Y-%m-%d")
        if not departure_date_hotel:
            departure_date_hotel = arrival_date
        
        # Search for flights if destination is provided
        flight_data = None
        if destination:
            try:
                flight_data = await flight_agent.search_flights(origin, destination, departure_date)
                rag_agent.set_flight_data(flight_data)
            except Exception as e:
                logging.warning(f"Could not fetch flight data: {e}")
        
        # Search for hotels if destination is provided
        hotel_data = None
        if destination:
            try:
                # Use a simplified destination ID mapping
                dest_id = "-1456928"  # Default destination ID
                hotel_data = await hotel_agent.search_hotels(
                    dest_id=dest_id,
                    search_type="CITY",
                    arrival_date=departure_date,
                    departure_date=departure_date_hotel,
                    adults=2
                )
                rag_agent.set_hotel_data(hotel_data)
            except Exception as e:
                logging.warning(f"Could not fetch hotel data: {e}")
        
        # Generate integrated itinerary
        result = await rag_agent.generate_itinerary(query)
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/rag/set-flight-data")
async def set_flight_data_for_rag(flight_data: dict):
    """Set flight data for RAG agent to use in itinerary generation"""
    try:
        agent = RAGAgent()
        agent.set_flight_data(flight_data)
        return {"success": True, "message": "Flight data set for RAG agent"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/rag/set-hotel-data")
async def set_hotel_data_for_rag(hotel_data: dict):
    """Set hotel data for RAG agent to use in itinerary generation"""
    try:
        agent = RAGAgent()
        agent.set_hotel_data(hotel_data)
        return {"success": True, "message": "Hotel data set for RAG agent"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/rag/add")
async def add_itinerary(
    title: str = Query(..., description="Title of the itinerary"),
    location: str = Query(..., description="Location of the itinerary"),
    content: str = Query(..., description="Content of the itinerary"),
    metadata: str = Query(None, description="Optional metadata in JSON format")
):
    agent = RAGAgent()
    metadata_dict = json.loads(metadata) if metadata else None
    result = await agent.add_itinerary(title, location, content, metadata_dict)
    return result

@app.get("/rag/{itinerary_id}")
async def get_itinerary(itinerary_id: str):
    agent = RAGAgent()
    result = await agent.get_itinerary_by_id(itinerary_id)
    return result

def preprocess_markdown(text: str) -> str:
    """Clean and format markdown text from Gemini for better frontend display"""
    
    # Remove excessive dashes/horizontal rules that don't render well
    text = re.sub(r'^-{3,}$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\*{3,}$', '', text, flags=re.MULTILINE)
    
    # Fix heading formatting - ensure space after # symbols
    text = re.sub(r'^(#{1,6})([^\s#])', r'\1 \2', text, flags=re.MULTILINE)
    
    # Ensure proper spacing around headings
    text = re.sub(r'\n(#{1,6}\s+[^\n]+)\n', r'\n\n\1\n\n', text)
    
    # Clean up multiple consecutive blank lines (max 2)
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    # Fix list formatting - ensure bullet points are properly formatted
    text = re.sub(r'^\*\s+', '• ', text, flags=re.MULTILINE)
    text = re.sub(r'^-\s+', '• ', text, flags=re.MULTILINE)
    
    # Ensure spacing before lists
    text = re.sub(r'([^\n])\n(• )', r'\1\n\n\2', text)
    
    # Clean up bold formatting
    text = re.sub(r'\*\*\*([^*]+)\*\*\*', r'**\1**', text)  # Triple asterisks to double
    
    # Add spacing after sections
    text = re.sub(r'(\*\*[^*]+\*\*:)\s*\n', r'\1\n\n', text)
    
    # Remove trailing whitespace from lines
    text = '\n'.join(line.rstrip() for line in text.split('\n'))
    
    # Trim overall
    text = text.strip()
    
    return text

@app.post("/chat")
async def chat(request: ChatRequest):
    """Chat endpoint using RAG agent"""
    try:
        logging.info(f"Received chat request: {request.message}")
        
        if not rag_agent:
            logging.error("RAG agent not initialized")
            raise HTTPException(status_code=500, detail="RAG agent not initialized. Check server logs.")
        
        response = rag_agent.get_response(request.message)
        
        # Preprocess the markdown response for better formatting
        response = preprocess_markdown(response)
        
        logging.info(f"Chat response generated successfully")
        
        return {"response": response}
    except FileNotFoundError as e:
        logging.error(f"PDF file not found: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Travel guide PDF not found: {str(e)}")
    except Exception as e:
        logging.error(f"Error in chat endpoint: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")

@app.get("/conversation/{user_id}")
async def get_conversation_history(user_id: str):
    """Get conversation history for a user"""
    history = orchestrator.get_conversation_history(user_id)
    return {"conversation_history": history}

@app.delete("/conversation/{user_id}")
async def clear_conversation_history(user_id: str):
    """Clear conversation history for a user"""
    orchestrator.clear_conversation_history(user_id)
    return {"message": "Conversation history cleared"}

# New API endpoint for frontend flight search
@app.post("/api/search-flights")
async def search_flights_api(request: dict):
    """Search flights API endpoint for frontend"""
    try:
        logging.info(f"Received flight search request: {request}")
        
        # Extract parameters from request body
        origin = request.get("origin")
        destination = request.get("destination")
        departure_date = request.get("departure_date")
        return_date = request.get("return_date")
        adults = request.get("adults", 1)
        children = request.get("children", 0)
        infants = request.get("infants", 0)
        
        logging.info(f"Extracted parameters - origin: {origin}, destination: {destination}, departure_date: {departure_date}, return_date: {return_date}, adults: {adults}, children: {children}, infants: {infants}")
        
        if not origin or not destination or not departure_date:
            return {
                "success": False,
                "error": "Missing required parameters: origin, destination, departure_date",
                "outbound_flights": [],
                "return_flights": []
            }
        
        flight_agent = FlightAgent()
        
        # Search for outbound flights (without return_date parameter)
        logging.info(f"Searching outbound flights from {origin} to {destination} on {departure_date}")
        outbound_flights = await flight_agent.search_flights(
            origin, destination, departure_date, None, adults, children, infants
        )
        logging.info(f"Outbound flights result: {outbound_flights}")
        
        # Search for return flights if return_date is provided
        return_flights = None
        if return_date:
            return_flights = await flight_agent.search_flights(
                destination, origin, return_date, None, adults, children, infants
            )
        
        # Format the response for frontend
        formatted_response = {
            "success": True,
            "outbound_flights": outbound_flights.get("data", []),
            "return_flights": return_flights.get("data", []) if return_flights else [],
            "meta": outbound_flights.get("meta", {}),
            "dictionaries": outbound_flights.get("dictionaries", {})
        }
        
        return formatted_response
        
    except Exception as e:
        logging.error(f"Flight search API error: {e}")
        return {
            "success": False,
            "error": str(e),
            "outbound_flights": [],
            "return_flights": []
        }

# New API endpoint for frontend hotel search
@app.post("/api/search-hotels")
async def search_hotels_api(request: dict):
    """Search hotels API endpoint for frontend"""
    try:
        logging.info(f"Received hotel search request: {request}")
        
        # Extract parameters from request body
        destination = request.get("destination")
        check_in = request.get("check_in")
        check_out = request.get("check_out")
        rooms = request.get("rooms", 1)
        adults = request.get("adults", 2)
        children = request.get("children", 0)
        
        logging.info(f"Extracted parameters - destination: {destination}, check_in: {check_in}, check_out: {check_out}, rooms: {rooms}, adults: {adults}, children: {children}")
        
        if not destination or not check_in or not check_out:
            return {
                "success": False,
                "error": "Missing required parameters: destination, check_in, check_out",
                "hotels": []
            }
        
        hotel_agent = HotelAgent()
        
        # Map destination names to coordinates for Amadeus API
        destination_mapping = {
            "mumbai, maharashtra": {"latitude": 19.0760, "longitude": 72.8777},
            "delhi": {"latitude": 28.7041, "longitude": 77.1025}, 
            "new delhi": {"latitude": 28.7041, "longitude": 77.1025},
            "bangalore, karnataka": {"latitude": 12.9716, "longitude": 77.5946},
            "chennai, tamil nadu": {"latitude": 13.0827, "longitude": 80.2707},
            "kolkata, west bengal": {"latitude": 22.5726, "longitude": 88.3639},
            "hyderabad, telangana": {"latitude": 17.3850, "longitude": 78.4867},
            "goa": {"latitude": 15.2993, "longitude": 74.1240},
            "pune, maharashtra": {"latitude": 18.5204, "longitude": 73.8567},
            "ahmedabad, gujarat": {"latitude": 23.0225, "longitude": 72.5714},
            "dubai, uae": {"latitude": 25.2048, "longitude": 55.2708},
            "london": {"latitude": 51.5074, "longitude": -0.1278},
            "paris": {"latitude": 48.8566, "longitude": 2.3522},
            "singapore": {"latitude": 1.3521, "longitude": 103.8198},
            "bangkok, thailand": {"latitude": 13.7563, "longitude": 100.5018}
        }
        
        # Get destination configuration from mapping, fallback to Mumbai
        dest_config = destination_mapping.get(destination.lower(), {"latitude": 19.0760, "longitude": 72.8777})
        latitude = dest_config["latitude"]
        longitude = dest_config["longitude"]
        
        logging.info(f"Searching hotels for destination: {destination} -> lat: {latitude}, lng: {longitude}")
        hotel_data = await hotel_agent.search_hotels(
            latitude=latitude,
            longitude=longitude,
            checkin=check_in,
            checkout=check_out,
            adults=adults,
            radius=50  # 50km radius
        )
        
        logging.info(f"Hotel search result: {hotel_data}")
        
        # Check if we have hotel data from Amadeus API
        hotels = hotel_data.get("data", []) if hotel_data.get("data") else []
        
        # No fallback needed - API is working and returning real data
        
        # Format the response for frontend
        formatted_response = {
            "success": True,
            "hotels": hotels,
            "meta": hotel_data.get("meta", {}),
            "search_params": {
                "destination": destination,
                "check_in": check_in,
                "check_out": check_out,
                "rooms": rooms,
                "adults": adults,
                "children": children
            },
            "message": f"Found {len(hotels)} hotels for {destination}" if hotels else f"No hotels available for {destination} on the selected dates"
        }
        
        return formatted_response
        
    except Exception as e:
        logging.error(f"Hotel search API error: {e}")
        return {
            "success": False,
            "error": str(e),
            "hotels": []
        }