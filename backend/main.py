import sys
import os
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

# Pydantic models for request/response
class ChatMessage(BaseModel):
    message: str
    user_id: str = None

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
    dest_id: str = Query(..., description="Destination ID for hotel search (e.g., city ID)"),
    search_type: str = Query("CITY", description="Search type (e.g., CITY)"),
    arrival_date: str = Query(..., description="Arrival date in YYYY-MM-DD format"),
    departure_date: str = Query(..., description="Departure date in YYYY-MM-DD format"),
    adults: int = Query(1, description="Number of adults"),
    children_age: str = Query("0,17", description="Comma-separated ages of children"),
    room_qty: int = Query(1, description="Number of rooms"),
    page_number: int = Query(1, description="Page number for results"),
    price_min: int = Query(0, description="Minimum price filter for search"),
    price_max: int = Query(0, description="Maximum price filter for search"),
    sort_by: str = Query(None, description="Sort by parameter"),
    categories_filter: str = Query(None, description="Categories filter parameter"),
    units: str = Query("metric", description="Units (metric/imperial)"),
    temperature_unit: str = Query("c", description="Temperature unit (c/f)"),
    languagecode: str = Query("en-us", description="Language code"),
    currency_code: str = Query("AED", description="Currency code"),
    location: str = Query("US", description="Location code")
):
    agent = HotelAgent()
    result = await agent.search_hotels(
        dest_id,
        search_type,
        arrival_date,
        departure_date,
        adults,
        children_age,
        room_qty,
        page_number,
        price_min,
        price_max,
        sort_by,
        categories_filter,
        units,
        temperature_unit,
        languagecode,
        currency_code,
        location
    )
    return result

@app.get("/rag")
async def rag_agent(query: str = Query(..., description="Itinerary or hotel query")):
    agent = RAGAgent()
    result = await agent.generate_itinerary(query)
    return result

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

# New chatbot endpoint
@app.post("/chat", response_model=ChatResponse)
async def chat_with_bot(chat_message: ChatMessage):
    """Main chatbot endpoint that coordinates all agents"""
    try:
        result = await orchestrator.process_message(chat_message.message, chat_message.user_id)
        return ChatResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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