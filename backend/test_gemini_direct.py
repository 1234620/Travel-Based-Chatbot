"""
Test Gemini LLM directly without embeddings
"""
import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAI

# Load environment variables
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(dotenv_path=env_path)

print("=" * 80)
print("Testing Google Gemini LLM Directly")
print("=" * 80)

gemini_api_key = os.getenv("gemini_api_key")
print(f"\n✓ API Key loaded: {gemini_api_key[:20]}...")

try:
    # Initialize Gemini LLM
    llm = GoogleGenerativeAI(
        google_api_key=gemini_api_key,
        model="gemini-1.5-flash",
        temperature=0.7
    )
    print("✓ Gemini Pro initialized successfully!")
    
    # Test with a simple query
    print("\nTesting query: 'Create a 3-day travel itinerary for Tokyo, Japan'")
    print("-" * 80)
    
    response = llm.invoke("Create a brief 3-day travel itinerary for Tokyo, Japan with luxury preferences. Keep it concise.")
    
    print("\n✅ Response from Gemini Pro:")
    print(response)
    print("\n" + "=" * 80)
    print("✅ Gemini LLM is working correctly!")
    print("=" * 80)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
