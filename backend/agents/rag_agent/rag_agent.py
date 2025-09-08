import os
import logging
from typing import List, Dict, Any, Optional
import json
from datetime import datetime, timedelta

from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_aws import BedrockEmbeddings, BedrockLLM
from langchain_community.vectorstores import FAISS
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class RAGAgent:
    def __init__(self,
                 local_pdf_path: Optional[str] = None,
                 aws_profile: str = "default"):
        self.aws_profile = aws_profile
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
        except Exception as e:
            logger.warning(f"Failed to initialize Bedrock components: {e}")
            self.initialization_error = str(e)
            # Continue without Bedrock - we'll use fallback responses

        # Initialize vector store with error handling
        try:
            self.vectorstore = self._build_index()
            self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": 4})
        except Exception as e:
            logger.warning(f"Failed to initialize vector store: {e}")
            self.vectorstore = None
            self.retriever = None

        # Prompt to allow augmentation beyond retrieved context, clearly marking augmented content
        self.qa_prompt = PromptTemplate(
            input_variables=["context", "question"],
            template=(
                "You are a helpful travel assistant.\n"
                "You are given context from a user's holiday itinerary and may also use your own general knowledge to add helpful, relevant details.\n"
                "Requirements:\n"
                "- First, answer grounded in the provided context when available.\n"
                "- Then, augment with additional helpful suggestions from your own knowledge.\n"
                "- Clearly separate sections as 'Grounded from Itinerary' and 'Augmented Suggestions'.\n"
                "- Do not invent specific facts (prices/schedules) unless commonly known and generic.\n"
                "- Keep the tone concise and actionable.\n\n"
                "Context:\n{context}\n\n"
                "Question: {question}\n\n"
                "Provide a structured answer with headings." 
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
        if not self.hotel_data or not self.hotel_data.get('data', {}).get('hotels'):
            return "No hotel information available."
        
        hotels = self.hotel_data['data']['hotels'][:5]  # Get top 5 hotels
        hotel_info = ""
        
        for i, hotel in enumerate(hotels, 1):
            property_info = hotel.get('property', {})
            name = property_info.get('name', 'N/A')
            rating = property_info.get('reviewScore', 'N/A')
            review_count = property_info.get('reviewCount', 0)
            price_breakdown = property_info.get('priceBreakdown', {})
            gross_price = price_breakdown.get('grossPrice', {})
            price = gross_price.get('value', 'N/A')
            currency = gross_price.get('currency', 'USD')
            quality_class = property_info.get('qualityClass', 0)
            
            # Format rating
            if rating != 'N/A' and rating > 0:
                rating_text = f"{rating}/10"
                if review_count > 0:
                    rating_text += f" ({review_count} reviews)"
            else:
                rating_text = "No rating available"
            
            # Format quality class
            stars = "⭐" * min(quality_class, 5) if quality_class > 0 else ""
            
            hotel_info += f"**{i}. {name}**\n"
            hotel_info += f"   {stars} {rating_text}\n"
            hotel_info += f"   💰 {price} {currency} per night\n"
            hotel_info += f"   🏨 Quality: {quality_class} stars\n\n"
        
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
            # Check if Bedrock is available
            if self.initialization_error or not self.qa_chain:
                return self._generate_fallback_itinerary(query)
            
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
            
            # Generate itinerary using the enhanced query
            result = self.qa_chain({"query": enhanced_query})
            answer = result.get("result", "")
            
            # Extract sources
            sources = []
            for d in result.get("source_documents", [])[:3]:
                meta = d.metadata or {}
                page = meta.get("page", "")
                source = meta.get("source", "") or meta.get("file_path", "")
                sources.append(f"{source}#page={page}" if page != "" else source)
            
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

    def _generate_fallback_itinerary(self, query: str) -> Dict[str, Any]:
        """Generate a basic itinerary when Bedrock is not available"""
        logger.info("Using fallback itinerary generation (Bedrock not available)")
        
        # Extract basic information
        location = self._extract_location(query)
        preferences = self._extract_preferences(query)
        
        # Create a comprehensive itinerary
        itinerary = f"🌍 **Complete Travel Plan for {location or 'your destination'}**\n\n"
        
        # Add flight information if available
        if self.flight_data and self.flight_data.get('data'):
            flight_info = self._format_flight_info()
            itinerary += f"✈️ **Available Flights:**\n{flight_info}\n\n"
        
        # Add hotel information if available
        if self.hotel_data and self.hotel_data.get('data', {}).get('hotels'):
            hotel_info = self._format_hotel_info()
            itinerary += f"🏨 **Available Hotels:**\n{hotel_info}\n\n"
        
        # Add detailed itinerary suggestions
        itinerary += "📅 **5-Day Itinerary:**\n\n"
        itinerary += "**Day 1: Arrival & Orientation**\n"
        itinerary += "• Arrive at destination airport\n"
        itinerary += "• Check into your hotel\n"
        itinerary += "• Explore the local area\n"
        itinerary += "• Enjoy a welcome dinner\n\n"
        
        itinerary += "**Day 2: City Exploration**\n"
        itinerary += "• Visit major landmarks and attractions\n"
        itinerary += "• Take a city tour or hop-on-hop-off bus\n"
        itinerary += "• Explore local markets and shopping areas\n"
        itinerary += "• Experience local cuisine\n\n"
        
        itinerary += "**Day 3: Cultural Immersion**\n"
        itinerary += "• Visit museums and cultural sites\n"
        itinerary += "• Take a guided walking tour\n"
        itinerary += "• Attend local events or performances\n"
        itinerary += "• Try authentic local experiences\n\n"
        
        itinerary += "**Day 4: Adventure & Relaxation**\n"
        itinerary += "• Outdoor activities or nature exploration\n"
        itinerary += "• Beach time or park visits\n"
        itinerary += "• Spa treatments or relaxation\n"
        itinerary += "• Evening entertainment\n\n"
        
        itinerary += "**Day 5: Departure**\n"
        itinerary += "• Final shopping or sightseeing\n"
        itinerary += "• Check out from hotel\n"
        itinerary += "• Transfer to airport\n"
        itinerary += "• Depart for home\n\n"
        
        if preferences:
            itinerary += f"🎯 **Your Preferences:** {', '.join(preferences)}\n\n"
        
        itinerary += "💡 **Travel Tips:**\n"
        itinerary += "• Book flights and hotels in advance for better rates\n"
        itinerary += "• Check local weather and pack accordingly\n"
        itinerary += "• Research local customs and etiquette\n"
        itinerary += "• Keep important documents and emergency contacts handy\n\n"
        
        itinerary += "📞 **Need Help?** Contact us for booking assistance or itinerary modifications!"
        
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
