"""
Quick test to verify Gemini generates detailed itineraries
"""
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from agents.rag_agent.rag_agent import RAGAgent


async def test_detailed_response():
    print("=" * 80)
    print("Testing Detailed Itinerary Generation with Gemini")
    print("=" * 80)
    
    # Initialize RAG agent
    rag_agent = RAGAgent(use_gemini=True)
    
    print(f"\n✓ LLM Available: {rag_agent.llm is not None}")
    print(f"✓ QA Chain Available: {rag_agent.qa_chain is not None}")
    print(f"✓ Initialization Error: {rag_agent.initialization_error}")
    
    # Test query
    query = "Create a romantic 4-day itinerary for Paris with luxury hotels and fine dining"
    
    print(f"\n{'='*80}")
    print(f"Query: {query}")
    print(f"{'='*80}\n")
    
    result = await rag_agent.generate_itinerary(query)
    
    itinerary = result.get('itinerary', '')
    print(f"Response Length: {len(itinerary)} characters")
    print(f"\nFirst 1000 characters:")
    print(itinerary[:1000])
    print("\n...")
    print(f"\nLast 500 characters:")
    print(itinerary[-500:])
    
    print(f"\n{'='*80}")
    print("✅ Test Complete!")
    print(f"{'='*80}")


if __name__ == "__main__":
    asyncio.run(test_detailed_response())
