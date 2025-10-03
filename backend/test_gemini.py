"""
Test script for RAG agent with Google Gemini
"""
import asyncio
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from agents.rag_agent.rag_agent import RAGAgent


async def test_gemini():
    print("=" * 80)
    print("Testing RAG Agent with Google Gemini")
    print("=" * 80)
    
    try:
        # Initialize RAG agent with Gemini
        print("\n1. Initializing RAG Agent with Gemini...")
        rag_agent = RAGAgent(use_gemini=True)
        print("✅ RAG Agent initialized successfully!")
        
        if rag_agent.initialization_error:
            print(f"⚠️ Warning: {rag_agent.initialization_error}")
            print("   Using fallback mode")
        else:
            print("✅ Gemini API initialized successfully!")
        
        # Test 1: Simple query
        print("\n" + "=" * 80)
        print("2. Testing simple itinerary generation...")
        print("=" * 80)
        query1 = "Create a 5-day luxury itinerary for Paris"
        result1 = await rag_agent.generate_itinerary(query1)
        
        print(f"\nQuery: {query1}")
        print(f"\nResponse:")
        print(result1.get('itinerary', 'No itinerary generated')[:500] + "...")
        print(f"\nLocation: {result1.get('location', 'N/A')}")
        print(f"Preferences: {result1.get('preferences', [])}")
        
        # Test 2: With flight data
        print("\n" + "=" * 80)
        print("3. Testing itinerary with flight data...")
        print("=" * 80)
        
        # Mock flight data
        flight_data = {
            'data': [{
                'price': {'total': '450.00', 'currency': 'USD'},
                'itineraries': [{
                    'duration': 'PT8H30M',
                    'segments': [{
                        'departure': {'iataCode': 'JFK', 'at': '2025-01-15T08:00:00'},
                        'arrival': {'iataCode': 'CDG', 'at': '2025-01-15T20:30:00'},
                        'carrierCode': 'AF',
                        'number': '007',
                        'aircraft': {'code': 'Boeing 777'}
                    }]
                }]
            }]
        }
        
        rag_agent.set_flight_data(flight_data)
        
        query2 = "Create a 3-day itinerary for Paris with the provided flights"
        result2 = await rag_agent.generate_itinerary(query2)
        
        print(f"\nQuery: {query2}")
        print(f"\nResponse:")
        print(result2.get('itinerary', 'No itinerary generated')[:500] + "...")
        
        # Test 3: With hotel data
        print("\n" + "=" * 80)
        print("4. Testing itinerary with hotel data...")
        print("=" * 80)
        
        # Mock hotel data
        hotel_data = {
            'data': {
                'hotels': [{
                    'property': {
                        'name': 'Le Grand Hotel Paris',
                        'reviewScore': 9.2,
                        'reviewCount': 1500,
                        'qualityClass': 5,
                        'priceBreakdown': {
                            'grossPrice': {'value': 350, 'currency': 'USD'}
                        }
                    }
                }]
            }
        }
        
        rag_agent.set_hotel_data(hotel_data)
        
        query3 = "Create a romantic 4-day itinerary for Paris with the provided flights and hotels"
        result3 = await rag_agent.generate_itinerary(query3)
        
        print(f"\nQuery: {query3}")
        print(f"\nResponse:")
        print(result3.get('itinerary', 'No itinerary generated')[:500] + "...")
        
        print("\n" + "=" * 80)
        print("✅ ALL TESTS COMPLETED SUCCESSFULLY!")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


if __name__ == "__main__":
    success = asyncio.run(test_gemini())
    sys.exit(0 if success else 1)
