"""
List available Gemini models and test with native library
"""
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
load_dotenv(dotenv_path=env_path)

print("=" * 80)
print("Testing Google Gemini with Native Library")
print("=" * 80)

gemini_api_key = os.getenv("gemini_api_key")
print(f"\n✓ API Key loaded: {gemini_api_key[:20]}...")

# Configure Gemini
genai.configure(api_key=gemini_api_key)

try:
    # List available models
    print("\nListing available Gemini models:")
    print("-" * 80)
    for model in genai.list_models():
        if 'generateContent' in model.supported_generation_methods:
            print(f"✓ {model.name}")
    
    # Test with gemini-2.5-flash
    print("\n" + "=" * 80)
    print("Testing with gemini-2.5-flash model:")
    print("-" * 80)
    
    model = genai.GenerativeModel('gemini-2.5-flash')
    response = model.generate_content("Create a brief 3-day travel itinerary for Tokyo, Japan with luxury preferences. Keep it concise (max 200 words).")
    
    print("\n✅ Response from Gemini:")
    print(response.text)
    print("\n" + "=" * 80)
    print("✅ Gemini API is working correctly!")
    print("=" * 80)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
