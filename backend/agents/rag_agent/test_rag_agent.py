import asyncio
import sys
import os

# Add the parent directory to sys.path to import the RAGAgent class
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agents.rag_agent.rag_agent import RAGAgent

async def test_rag_agent():
    print("Initializing RAG Agent...")
    agent = RAGAgent()
    
    # Test queries
    test_queries = [
        "I want a luxury vacation in the Maldives",
        "Looking for a family-friendly trip to New York",
        "Need a romantic getaway in the mountains",
        "Budget-friendly options in Paris"
    ]
    
    for query in test_queries:
        print(f"\n\nTesting query: {query}")
        result = await agent.generate_itinerary(query)
        
        print(f"Location detected: {result.get('location', 'None')}")
        print(f"Preferences detected: {', '.join(result.get('preferences', []))}")
        print(f"Sources used: {', '.join(result.get('sources', []))}")
        print("\nGenerated Itinerary:")
        print(result.get('itinerary', 'No itinerary generated'))

    # Test adding a new itinerary
    print("\n\nTesting adding a new itinerary...")
    add_result = await agent.add_itinerary(
        title="Cultural Tour of Japan",
        location="Tokyo",
        content="Day 1: Check-in at the Park Hyatt Tokyo. Visit Meiji Shrine and Shinjuku Gyoen National Garden.\n"
               "Day 2: Morning at the Tokyo National Museum. Afternoon exploring Asakusa and Senso-ji Temple.\n"
               "Day 3: Day trip to Kamakura to see the Great Buddha. Evening food tour in Shibuya.\n"
               "Day 4: Visit teamLab Borderless digital art museum. Shopping in Ginza. Farewell dinner at a traditional izakaya.",
        metadata={"tags": ["cultural", "city", "food"], "difficulty": "easy"}
    )
    print(f"Add result: {add_result}")
    
    if "id" in add_result:
        # Test retrieving the added itinerary
        print(f"\nRetrieving added itinerary with ID: {add_result['id']}")
        get_result = await agent.get_itinerary_by_id(add_result['id'])
        print(f"Retrieved itinerary: {get_result}")
        
        # Test generating an itinerary with the new content
        print("\nTesting query with newly added content:")
        new_query = "I want to explore Japanese culture in Tokyo"
        new_result = await agent.generate_itinerary(new_query)
        print(f"Generated itinerary for '{new_query}':")
        print(new_result.get('itinerary', 'No itinerary generated'))

if __name__ == "__main__":
    asyncio.run(test_rag_agent())