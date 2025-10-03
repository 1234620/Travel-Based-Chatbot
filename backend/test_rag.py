"""
Simple test script for RAG agent
"""
import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents.rag_agent.rag_agent import RAGAgent
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))

async def test_rag_agent():
    print("=" * 50)
    print("Testing RAG Agent Initialization")
    print("=" * 50)
    
    try:
        # Initialize RAG agent
        print("\n1. Initializing RAG Agent...")
        agent = RAGAgent()
        
        # Check initialization
        if agent.initialization_error:
            print(f"❌ Initialization failed: {agent.initialization_error}")
            return False
        else:
            print("✓ RAG Agent initialized successfully")
        
        # Test simple query
        print("\n2. Testing simple itinerary generation...")
        query = "Plan a 3-day trip to Paris with museums and good food"
        print(f"Query: {query}")
        
        result = await agent.generate_itinerary(query)
        
        if "error" in result:
            print(f"❌ Generation failed: {result['error']}")
            return False
        else:
            print("✓ Itinerary generated successfully")
            print(f"\nItinerary preview (first 200 chars):")
            print("-" * 50)
            itinerary_text = result.get("itinerary", "No itinerary found")
            print(itinerary_text[:200] + "..." if len(itinerary_text) > 200 else itinerary_text)
            print("-" * 50)
        
        print("\n3. Testing with flight and hotel data...")
        # Set sample flight data
        flight_data = {
            "data": [
                {
                    "price": {"total": "500.00", "currency": "USD"},
                    "itineraries": [
                        {
                            "segments": [
                                {
                                    "departure": {"iataCode": "NYC", "at": "2024-10-15T08:00:00"},
                                    "arrival": {"iataCode": "CDG", "at": "2024-10-15T20:00:00"}
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        agent.set_flight_data(flight_data)
        print("✓ Flight data set")
        
        # Set sample hotel data
        hotel_data = {
            "data": [
                {
                    "name": "Paris Luxury Hotel",
                    "rating": "5",
                    "price": {"total": "200.00", "currency": "USD"}
                }
            ]
        }
        agent.set_hotel_data(hotel_data)
        print("✓ Hotel data set")
        
        # Generate itinerary with data
        query_with_data = "Create a detailed 3-day Paris itinerary including my flight and hotel"
        result_with_data = await agent.generate_itinerary(query_with_data)
        
        if "error" in result_with_data:
            print(f"❌ Generation with data failed: {result_with_data['error']}")
            return False
        else:
            print("✓ Itinerary with flight/hotel data generated successfully")
        
        print("\n" + "=" * 50)
        print("✅ All RAG agent tests passed!")
        print("=" * 50)
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with exception: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_rag_agent())
    sys.exit(0 if success else 1)
