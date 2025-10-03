import os
import logging
from typing import List, Dict, Any, Optional
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables from .env file (project root)
# __file__ is in backend/agents/rag_agent/rag_agent.py
# Go up 3 levels: rag_agent -> agents -> backend -> project root
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), '.env')
load_dotenv(dotenv_path=env_path)

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_aws import BedrockEmbeddings, BedrockLLM
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class RAGAgent:
    def __init__(self,
                 local_pdf_path: Optional[str] = None,
                 aws_profile: str = "default",
                 use_gemini: bool = True):
        self.aws_profile = aws_profile
        self.use_gemini = use_gemini
        # Use local itinerary PDF (e.g., Holiday_Itinerary_Book.pdf)
        self.local_pdf_path = local_pdf_path or os.path.join(os.getcwd(), "Holiday_Itinerary_Book.pdf")
        
        # Store flight and hotel data for itinerary generation
        self.flight_data = None
        self.hotel_data = None
        
        # Initialize components with error handling
        self.text_splitter = None
        self.embeddings = None
        self.llm = None
        self.vector_store = None
        self.qa_chain = None
        self.initialization_error = None
        
        try:
            # Build vector index from the provided PDF
            self.text_splitter = RecursiveCharacterTextSplitter(
                separators=["\n\n", "\n", " ", ""],
                chunk_size=400,
                chunk_overlap=20
            )

            if self.use_gemini:
                # Use Google Gemini for embeddings and LLM
                gemini_api_key = os.getenv("gemini_api_key") or os.getenv("GEMINI_API_KEY")
                if not gemini_api_key or gemini_api_key == "your_gemini_api_key_here":
                    raise ValueError(f"Gemini API key not set in environment variables. Checked: gemini_api_key={os.getenv('gemini_api_key')}, GEMINI_API_KEY={os.getenv('GEMINI_API_KEY')}")
                
                # Use text-embedding-004 which is available in the free tier
                self.embeddings = GoogleGenerativeAIEmbeddings(
                    google_api_key=gemini_api_key,
                    model="models/text-embedding-004"
                )

                self.llm = ChatGoogleGenerativeAI(
                    google_api_key=gemini_api_key,
                    model="gemini-2.5-flash",
                    temperature=0.7,
                    max_tokens=4000
                )
                logger.info("Initialized with Google Gemini 2.5 Flash")
            else:
                # Fallback to AWS Bedrock
                self.embeddings = BedrockEmbeddings(
                    credentials_profile_name=self.aws_profile,
                    model_id='amazon.titan-embed-text-v1'
                )

                self.llm = BedrockLLM(
                    credentials_profile_name=self.aws_profile,
                    model='amazon.titan-text-lite-v1',
                    model_kwargs={
                        "maxTokenCount": 3000,
                        "temperature": 0.1,
                        "topP": 0.9
                    }
                )
                logger.info("Initialized with AWS Bedrock")
        except Exception as e:
            logger.warning(f"Failed to initialize AI components: {e}")
            self.initialization_error = str(e)
            # Continue without AI - we'll use fallback responses

        # Initialize vector store with error handling
        try:
            self.vectorstore = self._build_index()
            self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": 4})
        except Exception as e:
            logger.warning(f"Failed to initialize vector store: {e}")
            self.vectorstore = None
            self.retriever = None

        # Enhanced prompt optimized for GPT-5
        self.qa_prompt = PromptTemplate(
            input_variables=["context", "question"],
            template=(
                "You are an expert travel assistant with comprehensive knowledge of destinations worldwide. "
                "Create detailed, personalized travel itineraries based on the user's request.\n\n"
                "Context from travel database:\n{context}\n\n"
                "User Request: {question}\n\n"
                "Instructions:\n"
                "1. Create a comprehensive, day-by-day itinerary based on the user's specific request\n"
                "2. Include practical details like transportation, timing, and costs where relevant\n"
                "3. Add cultural insights, local tips, and must-see attractions\n"
                "4. Consider the user's preferences (budget/luxury, cultural/adventure, etc.)\n"
                "5. Provide specific restaurant and activity recommendations\n"
                "6. Include travel tips, weather considerations, and local customs\n"
                "7. Make the itinerary actionable with clear daily schedules\n\n"
                "Format your response as a detailed travel itinerary with clear sections and bullet points."
            ),
        )

        # Initialize QA chain with error handling
        try:
            if self.llm and self.retriever:
                self.qa_chain = RetrievalQA.from_chain_type(
                    llm=self.llm,
                    chain_type="stuff",
                    retriever=self.retriever,
                    return_source_documents=True,
                    chain_type_kwargs={"prompt": self.qa_prompt}
                )
            else:
                self.qa_chain = None
                logger.warning("QA chain not initialized - missing LLM or retriever")
        except Exception as e:
            logger.warning(f"Failed to initialize QA chain: {e}")
            self.qa_chain = None
    
    def set_flight_data(self, flight_data: Dict[str, Any]):
        """Set flight data for itinerary generation"""
        self.flight_data = flight_data
        logger.info("Flight data set for itinerary generation")
    
    def set_hotel_data(self, hotel_data: Dict[str, Any]):
        """Set hotel data for itinerary generation"""
        self.hotel_data = hotel_data
        logger.info("Hotel data set for itinerary generation")
    
    def _format_flight_info(self) -> str:
        """Format flight data for inclusion in itinerary"""
        if not self.flight_data or not self.flight_data.get('data'):
            return "No flight information available."
        
        flights = self.flight_data['data'][:5]  # Get top 5 flights
        flight_info = ""
        
        for i, flight in enumerate(flights, 1):
            price = flight.get('price', {})
            itinerary = flight.get('itineraries', [{}])[0]
            segments = itinerary.get('segments', [])
            
            if segments:
                departure = segments[0].get('departure', {})
                arrival = segments[-1].get('arrival', {})
                carrier_code = segments[0].get('carrierCode', 'N/A')
                flight_number = segments[0].get('number', 'N/A')
                
                # Format departure and arrival times
                dep_time = departure.get('at', 'N/A')
                arr_time = arrival.get('at', 'N/A')
                if dep_time != 'N/A' and 'T' in dep_time:
                    dep_time = dep_time.split('T')[1][:5]  # Extract time only
                if arr_time != 'N/A' and 'T' in arr_time:
                    arr_time = arr_time.split('T')[1][:5]  # Extract time only
                
                flight_info += f"**{i}. {carrier_code} {flight_number}**\n"
                flight_info += f"   🛫 {departure.get('iataCode', 'N/A')} → {arrival.get('iataCode', 'N/A')}\n"
                flight_info += f"   ⏰ {dep_time} → {arr_time}\n"
                flight_info += f"   💰 {price.get('total', 'N/A')} {price.get('currency', 'USD')}\n"
                flight_info += f"   ⏱️ Duration: {itinerary.get('duration', 'N/A')}\n"
                flight_info += f"   🛩️ Aircraft: {segments[0].get('aircraft', {}).get('code', 'N/A')}\n\n"
        
        return flight_info
    
    def _format_hotel_info(self) -> str:
        """Format hotel data for inclusion in itinerary"""
        if not self.hotel_data or not self.hotel_data.get('data'):
            return "No hotel information available."
        
        # Handle both list and dict formats
        hotels_data = self.hotel_data.get('data', [])
        if isinstance(hotels_data, dict):
            hotels = hotels_data.get('hotels', [])[:5]
        else:
            hotels = hotels_data[:5] if isinstance(hotels_data, list) else []
        
        if not hotels:
            return "No hotel information available."
        
        hotel_info = ""
        
        for i, hotel in enumerate(hotels, 1):
            property_info = hotel.get('property', {})
            name = property_info.get('name', hotel.get('name', 'N/A'))
            rating = property_info.get('reviewScore', hotel.get('rating', 'N/A'))
            review_count = property_info.get('reviewCount', hotel.get('reviewCount', 0))
            price_breakdown = property_info.get('priceBreakdown', {})
            gross_price = price_breakdown.get('grossPrice', hotel.get('price', {}))
            price = gross_price.get('value', 'N/A')
            currency = gross_price.get('currency', 'USD')
            quality_class = property_info.get('qualityClass', 0)
            
            # Convert to numeric types safely
            try:
                rating_num = float(rating) if rating != 'N/A' else 0
                review_count_num = int(review_count) if review_count else 0
                quality_class_num = int(quality_class) if quality_class else 0
            except (ValueError, TypeError):
                rating_num = 0
                review_count_num = 0
                quality_class_num = 0
            
            # Format rating
            if rating_num > 0:
                rating_text = f"{rating_num}/10"
                if review_count_num > 0:
                    rating_text += f" ({review_count_num} reviews)"
            else:
                rating_text = "No rating available"
            
            # Format quality class
            stars = "⭐" * min(quality_class_num, 5) if quality_class_num > 0 else ""
            
            hotel_info += f"**{i}. {name}**\n"
            hotel_info += f"   {stars} {rating_text}\n"
            hotel_info += f"   💰 {price} {currency} per night\n"
            hotel_info += f"   🏨 Quality: {quality_class_num} stars\n\n"
        
        return hotel_info

    def _build_index(self):
        try:
            if self.local_pdf_path and os.path.exists(self.local_pdf_path):
                loader = PyPDFLoader(self.local_pdf_path)
                docs = loader.load()
                logger.info(f"Loaded PDF from: {self.local_pdf_path}")
            else:
                logger.warning(f"Local PDF not found at: {self.local_pdf_path}")
                # Build from a small fallback text snippet to keep system usable
                from langchain.schema import Document
                docs = [Document(page_content=(
                    "Welcome to the most comprehensive guide on Amazon Bedrock and Generative AI on AWS from a "
                    "practising AWS Solution Architect and best-selling Udemy Instructor."))]

            split_docs = self.text_splitter.split_documents(docs)
            vectorstore = FAISS.from_documents(split_docs, self.embeddings)
            logger.info("Vector index built with FAISS using Bedrock Titan embeddings")
            return vectorstore
        except Exception as e:
            logger.error(f"Failed to build index: {e}")
            # Return empty FAISS index as fallback
            from langchain.schema import Document
            docs = [Document(page_content="Fallback content")]
            split_docs = self.text_splitter.split_documents(docs)
            return FAISS.from_documents(split_docs, self.embeddings)

    async def retrieve_documents(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        try:
            docs = self.retriever.get_relevant_documents(query)
            results: List[Dict[str, Any]] = []
            for d in docs[:top_k]:
                results.append({
                    "content": d.page_content,
                    "metadata": d.metadata
                })
            return results
        except Exception as e:
            logger.error(f"Error retrieving documents: {e}")
            return []

    async def generate_itinerary(self, query: str) -> Dict[str, Any]:
        try:
            # Create enhanced query with flight and hotel data
            enhanced_query = query
            
            # Add flight information if available
            if self.flight_data:
                flight_info = self._format_flight_info()
                enhanced_query += f"\n\nFlight Information:\n{flight_info}"
            
            # Add hotel information if available
            if self.hotel_data:
                hotel_info = self._format_hotel_info()
                enhanced_query += f"\n\nHotel Information:\n{hotel_info}"
            
            # If we have Gemini LLM but QA chain failed (due to embedding quota), use LLM directly
            if self.llm and not self.qa_chain:
                logger.info("Using Gemini LLM directly (QA chain not available)")
                prompt = (
                    "You are an expert travel assistant with comprehensive knowledge of destinations worldwide. "
                    "Create detailed, personalized travel itineraries based on the user's request.\n\n"
                    f"User Request: {enhanced_query}\n\n"
                    "Instructions:\n"
                    "1. Create a comprehensive, day-by-day itinerary based on the user's specific request\n"
                    "2. Include practical details like transportation, timing, and costs where relevant\n"
                    "3. Add cultural insights, local tips, and must-see attractions\n"
                    "4. Consider the user's preferences (budget/luxury, cultural/adventure, etc.)\n"
                    "5. Provide specific restaurant and activity recommendations\n"
                    "6. Include travel tips, weather considerations, and local customs\n"
                    "7. Make the itinerary actionable with clear daily schedules\n"
                    "8. If flight and hotel information is provided, integrate it naturally into the itinerary\n\n"
                    "Format your response as a detailed travel itinerary with clear sections and bullet points."
                )
                answer = self.llm.invoke(prompt).content
                sources = []
            elif self.qa_chain:
                # Use QA chain with RAG if available
                logger.info("Using QA chain with RAG retrieval")
                result = self.qa_chain({"query": enhanced_query})
                answer = result.get("result", "")
                # Extract sources
                sources = []
                for d in result.get("source_documents", [])[:3]:
                    meta = d.metadata or {}
                    page = meta.get("page", "")
                    source = meta.get("source", "") or meta.get("file_path", "")
                    sources.append(f"{source}#page={page}" if page != "" else source)
            else:
                # Fallback if no LLM available
                return self._generate_fallback_itinerary(query)
            
            # Extract location and preferences from the query
            location = self._extract_location(query)
            preferences = self._extract_preferences(query)
            
            return {
                "itinerary": answer,
                "location": location,
                "preferences": preferences,
                "sources": sources,
                "flight_data": self.flight_data,
                "hotel_data": self.hotel_data
            }
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return {"error": str(e), "itinerary": "An error occurred while generating your response."}
    
    def _extract_location(self, query: str) -> str:
        """Extract location from query using simple keyword matching"""
        query_lower = query.lower()
        
        # Common destination keywords
        destinations = {
            'paris': 'Paris, France',
            'london': 'London, UK',
            'new york': 'New York, USA',
            'tokyo': 'Tokyo, Japan',
            'dubai': 'Dubai, UAE',
            'singapore': 'Singapore',
            'bangkok': 'Bangkok, Thailand',
            'rome': 'Rome, Italy',
            'barcelona': 'Barcelona, Spain',
            'amsterdam': 'Amsterdam, Netherlands',
            'maldives': 'Maldives',
            'bali': 'Bali, Indonesia',
            'sydney': 'Sydney, Australia',
            'mumbai': 'Mumbai, India',
            'istanbul': 'Istanbul, Turkey'
        }
        
        for keyword, location in destinations.items():
            if keyword in query_lower:
                return location
        
        return "Not specified"
    
    def _extract_preferences(self, query: str) -> List[str]:
        """Extract travel preferences from query"""
        query_lower = query.lower()
        preferences = []
        
        # Luxury indicators
        luxury_keywords = ['luxury', 'premium', '5-star', 'high-end', 'exclusive', 'deluxe']
        if any(keyword in query_lower for keyword in luxury_keywords):
            preferences.append('luxury')
        
        # Budget indicators
        budget_keywords = ['budget', 'cheap', 'affordable', 'economy', 'low-cost']
        if any(keyword in query_lower for keyword in budget_keywords):
            preferences.append('budget')
        
        # Activity preferences
        activity_keywords = {
            'beach': ['beach', 'coastal', 'seaside', 'ocean'],
            'cultural': ['cultural', 'museum', 'history', 'heritage', 'art'],
            'adventure': ['adventure', 'hiking', 'outdoor', 'extreme', 'sports'],
            'romantic': ['romantic', 'honeymoon', 'couple', 'intimate'],
            'family': ['family', 'kids', 'children', 'family-friendly'],
            'business': ['business', 'corporate', 'meeting', 'conference']
        }
        
        for preference, keywords in activity_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                preferences.append(preference)
        
        return preferences

    def _extract_duration(self, query: str) -> int:
        """Extract trip duration from query"""
        query_lower = query.lower()
        
        # Look for duration keywords
        if any(word in query_lower for word in ['weekend', '2-day', 'two day']):
            return 2
        elif any(word in query_lower for word in ['3-day', 'three day', '3 days']):
            return 3
        elif any(word in query_lower for word in ['4-day', 'four day', '4 days']):
            return 4
        elif any(word in query_lower for word in ['5-day', 'five day', '5 days']):
            return 5
        elif any(word in query_lower for word in ['week', '7-day', 'seven day', '7 days']):
            return 7
        elif any(word in query_lower for word in ['10-day', 'ten day', '10 days']):
            return 10
        elif any(word in query_lower for word in ['2 weeks', 'two weeks', '14 days']):
            return 14
        else:
            return 5  # Default to 5 days

    def _get_location_specific_content(self, location: str) -> Dict[str, str]:
        """Get location-specific content and tips"""
        if not location or location == "Not specified":
            return {"intro": "", "tips": ""}
        
        location_data = {
            "Tokyo, Japan": {
                "intro": "Tokyo is a vibrant metropolis blending ancient traditions with cutting-edge technology. Experience everything from serene temples to bustling neon-lit districts.",
                "tips": "• Use JR Pass for unlimited train travel\n• Try street food in Tsukiji Outer Market\n• Visit during cherry blossom season (March-April)\n• Learn basic Japanese phrases"
            },
            "Paris, France": {
                "intro": "The City of Light offers world-class art, cuisine, and architecture. From the Eiffel Tower to charming cafes, Paris is perfect for romance and culture.",
                "tips": "• Purchase a Paris Pass for museum access\n• Try authentic croissants and café au lait\n• Visit during spring (April-June) for best weather\n• Learn basic French greetings"
            },
            "New York, USA": {
                "intro": "The Big Apple never sleeps! Experience Broadway shows, world-famous landmarks, diverse neighborhoods, and incredible food from around the globe.",
                "tips": "• Get a MetroCard for subway transportation\n• Try pizza in Brooklyn and bagels in Manhattan\n• Visit during fall (September-November) for pleasant weather\n• Book Broadway shows in advance"
            },
            "London, UK": {
                "intro": "Rich in history and culture, London offers royal palaces, world-class museums, and charming pubs. Experience both tradition and modernity.",
                "tips": "• Get an Oyster card for public transport\n• Try traditional fish and chips\n• Visit during summer (June-August) for best weather\n• Book attractions like London Eye in advance"
            },
            "Dubai, UAE": {
                "intro": "A futuristic city in the desert, Dubai offers luxury shopping, world-class architecture, and unique desert experiences.",
                "tips": "• Visit during winter (November-March) to avoid extreme heat\n• Try authentic Emirati cuisine\n• Book desert safari experiences\n• Respect local customs and dress modestly"
            },
            "Bangkok, Thailand": {
                "intro": "A city of contrasts with ancient temples, bustling markets, and vibrant street food culture. Experience authentic Thai hospitality.",
                "tips": "• Use tuk-tuks and river boats for transportation\n• Try street food (pad thai, mango sticky rice)\n• Visit during cool season (November-February)\n• Bargain at markets but be respectful"
            },
            "Mumbai, India": {
                "intro": "India's financial capital offers a mix of colonial architecture, Bollywood glamour, and incredible street food. Experience the energy of Maximum City.",
                "tips": "• Try local street food (vada pav, bhel puri)\n• Visit during winter (October-March) for pleasant weather\n• Use local trains and taxis for transportation\n• Book hotels in advance during peak season"
            }
        }
        
        return location_data.get(location, {"intro": "", "tips": ""})

    def _generate_daily_plans(self, location: str, preferences: List[str], duration: int, location_specific: Dict[str, str]) -> str:
        """Generate dynamic daily plans based on location and preferences"""
        plans = ""
        
        # Define activity types based on preferences
        cultural_activities = ["Visit museums and cultural sites", "Explore historical landmarks", "Take guided walking tours", "Attend local performances"]
        adventure_activities = ["Outdoor activities and nature exploration", "Adventure sports and hiking", "Water activities", "Mountain or beach exploration"]
        luxury_activities = ["Fine dining experiences", "Luxury spa treatments", "Premium shopping", "Exclusive cultural events"]
        budget_activities = ["Free walking tours", "Local market exploration", "Public parks and gardens", "Street food experiences"]
        
        # Generate activities based on preferences
        if "cultural" in preferences:
            primary_activities = cultural_activities
        elif "adventure" in preferences:
            primary_activities = adventure_activities
        elif "luxury" in preferences:
            primary_activities = luxury_activities
        elif "budget" in preferences:
            primary_activities = budget_activities
        else:
            primary_activities = cultural_activities + adventure_activities[:2]  # Mix for general travel
        
        # Generate daily plans
        for day in range(1, duration + 1):
            plans += f"**Day {day}:**\n"
            
            if day == 1:
                plans += "• Arrive at destination airport\n"
                plans += "• Check into your hotel\n"
                plans += "• Explore the local area and get oriented\n"
                plans += "• Enjoy a welcome dinner\n\n"
            elif day == duration:
                plans += "• Final shopping or sightseeing\n"
                plans += "• Check out from hotel\n"
                plans += "• Transfer to airport\n"
                plans += "• Depart for home\n\n"
            else:
                # Vary activities for middle days
                activity_index = (day - 2) % len(primary_activities)
                primary_activity = primary_activities[activity_index]
                
                plans += f"• {primary_activity}\n"
                plans += "• Experience local cuisine and culture\n"
                plans += "• Explore unique neighborhood attractions\n"
                plans += "• Relax and enjoy evening entertainment\n\n"
        
        return plans

    def _get_preference_tips(self, preferences: List[str], location: str) -> str:
        """Get preference-specific recommendations"""
        tips = []
        
        if "luxury" in preferences:
            tips.append("• Book premium hotels and restaurants in advance")
            tips.append("• Consider private tours and experiences")
            tips.append("• Look for VIP access to popular attractions")
        
        if "budget" in preferences:
            tips.append("• Use public transportation and walking")
            tips.append("• Eat at local markets and street food stalls")
            tips.append("• Look for free walking tours and museum days")
        
        if "cultural" in preferences:
            tips.append("• Book museum passes for multiple attractions")
            tips.append("• Research local festivals and cultural events")
            tips.append("• Learn basic phrases in the local language")
        
        if "adventure" in preferences:
            tips.append("• Pack appropriate gear for outdoor activities")
            tips.append("• Book adventure tours and experiences")
            tips.append("• Check weather conditions and safety requirements")
        
        if "romantic" in preferences:
            tips.append("• Book romantic restaurants and experiences")
            tips.append("• Consider sunset tours and scenic viewpoints")
            tips.append("• Look for couples' spa packages")
        
        if "family" in preferences:
            tips.append("• Choose family-friendly accommodations")
            tips.append("• Plan activities suitable for all ages")
            tips.append("• Book attractions with family packages")
        
        return "\n".join(tips) if tips else ""

    def _generate_fallback_itinerary(self, query: str) -> Dict[str, Any]:
        """Generate a dynamic itinerary when Bedrock is not available"""
        logger.info("Using fallback itinerary generation (Bedrock not available)")
        
        # Extract basic information
        location = self._extract_location(query)
        preferences = self._extract_preferences(query)
        
        # Determine trip duration from query
        duration = self._extract_duration(query)
        
        # Create location-specific content
        location_specific = self._get_location_specific_content(location)
        
        # Create a comprehensive itinerary
        itinerary = f"**Complete Travel Plan for {location or 'your destination'}**\n\n"
        
        # Add flight information if available
        if self.flight_data and self.flight_data.get('data'):
            flight_info = self._format_flight_info()
            itinerary += f"**Available Flights:**\n{flight_info}\n\n"
        
        # Add hotel information if available
        if self.hotel_data and self.hotel_data.get('data'):
            hotel_info = self._format_hotel_info()
            itinerary += f"**Available Hotels:**\n{hotel_info}\n\n"
        
        # Add location-specific introduction
        if location_specific['intro']:
            itinerary += f"**About {location}:**\n{location_specific['intro']}\n\n"
        
        # Add detailed itinerary suggestions
        itinerary += f"**{duration}-Day Itinerary:**\n\n"
        
        # Generate dynamic daily plans based on location and preferences
        daily_plans = self._generate_daily_plans(location, preferences, duration, location_specific)
        itinerary += daily_plans
        
        if preferences:
            itinerary += f"**Your Preferences:** {', '.join(preferences)}\n\n"
            
            # Add preference-specific recommendations
            preference_tips = self._get_preference_tips(preferences, location)
            if preference_tips:
                itinerary += f"**Personalized Recommendations:**\n{preference_tips}\n\n"
        
        # Add location-specific tips
        if location_specific['tips']:
            itinerary += f"**{location} Travel Tips:**\n{location_specific['tips']}\n\n"
        
        itinerary += "**General Travel Tips:**\n"
        itinerary += "• Book flights and hotels in advance for better rates\n"
        itinerary += "• Check local weather and pack accordingly\n"
        itinerary += "• Research local customs and etiquette\n"
        itinerary += "• Keep important documents and emergency contacts handy\n\n"
        
        itinerary += "**Need Help?** Contact us for booking assistance or itinerary modifications!"
        
        return {
            "itinerary": itinerary,
            "location": location,
            "preferences": preferences,
            "sources": [],
            "flight_data": self.flight_data,
            "hotel_data": self.hotel_data
        }

    # Legacy endpoints kept for API compatibility
    async def add_itinerary(self, title: str, location: str, content: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return {"error": "Not supported in Bedrock-based RAG. Use document ingestion via PDF index."}

    async def get_itinerary_by_id(self, itinerary_id: str) -> Dict[str, Any]:
        return {"error": "Not supported in Bedrock-based RAG."}
