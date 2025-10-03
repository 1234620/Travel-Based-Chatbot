#!/usr/bin/env python3
"""
Test the RAG agent with GPT-5 integration
"""
import asyncio
import sys
import os
from dotenv import load_dotenv

# Load environment variables from .env file (project root)
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
print(f"Debug: Looking for .env file at: {env_path}")
print(f"Debug: .env file exists: {os.path.exists(env_path)}")
load_dotenv(dotenv_path=env_path)

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agents.rag_agent.rag_agent import RAGAgent

async def test_gpt5_rag():
    """Test the RAG agent with GPT-5"""
    print("Testing RAG Agent with GPT-5...")
    
    # Check if API key is set
    api_key = os.getenv("openai_api_key") or os.getenv("OPENAI_API_KEY")
    print(f"Debug: Found API key: {api_key[:20] if api_key else 'None'}...")
    
    if not api_key or api_key == "your_gpt5_api_key_here":
        print("ERROR: OpenAI API key not set! Please add your GPT-5 API key to the .env file.")
        print("Add this line to your .env file:")
        print("   openai_api_key=your_actual_gpt5_api_key_here")
        return False
    
    try:
        # Create RAG agent instance with GPT-5
        agent = RAGAgent(use_openai=True)
        
        if agent.initialization_error:
            print(f"ERROR: Initialization error: {agent.initialization_error}")
            return False
        
        print("SUCCESS: RAG Agent initialized successfully with GPT-5!")
        
        # Test with a simple query
        query = "Plan a 3-day luxury trip to Tokyo, Japan"
        print(f"\nTesting query: {query}")
        
        # Generate itinerary
        result = await agent.generate_itinerary(query)
        
        if "error" in result:
            print(f"ERROR: {result['error']}")
            return False
        else:
            print("SUCCESS: Generated itinerary with GPT-5:")
            print("=" * 60)
            print(result.get("itinerary", "No itinerary generated"))
            print("=" * 60)
            
            if result.get("location"):
                print(f"Location: {result['location']}")
            if result.get("preferences"):
                print(f"Preferences: {result['preferences']}")
            
            return True
            
    except Exception as e:
        print(f"ERROR: Error testing RAG agent: {str(e)}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_gpt5_rag())
    
    if result:
        print("\nGPT-5 RAG agent test completed successfully!")
        print("Your RAG agent is now powered by GPT-5!")
    else:
        print("\nGPT-5 RAG agent test failed!")
        print("Make sure to set your openai_api_key in the .env file")
