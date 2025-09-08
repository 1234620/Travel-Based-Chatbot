# RAG Agent for Hotel Itineraries

## Overview
The Retrieval-Augmented Generation (RAG) Agent is designed to generate personalized hotel itineraries by combining pre-trained language models with document retrieval from Elasticsearch. This agent enhances the capabilities of the multi-agent chatbot by providing rich, contextually relevant itineraries based on user queries.

## Features
- **Semantic Search**: Uses sentence embeddings to find relevant itineraries based on meaning, not just keywords
- **Hybrid Retrieval**: Combines semantic and keyword-based search for optimal results
- **Personalization**: Extracts location and preferences from user queries
- **Fallback Mechanisms**: Generates generic itineraries when no relevant documents are found
- **Document Management**: Supports adding new itineraries to the knowledge base

## Setup Requirements

### Dependencies
- Elasticsearch (v8.0.0 or higher)
- Transformers library (v4.30.0 or higher)
- Sentence-Transformers (v2.2.0 or higher)
- PyTorch (v2.0.0 or higher)

### Environment Variables
- `ELASTICSEARCH_URL`: URL for the Elasticsearch instance (default: "http://localhost:9200")

## API Endpoints

### Generate Itinerary
```
GET /rag?query={query}
```
Generates a personalized hotel itinerary based on the user's query.

### Add Itinerary
```
POST /rag/add?title={title}&location={location}&content={content}&metadata={metadata}
```
Adds a new itinerary to the Elasticsearch index.

### Get Itinerary by ID
```
GET /rag/{itinerary_id}
```
Retrieves a specific itinerary by its ID.

## Implementation Details

### Elasticsearch Index
The agent creates an index called `hotel_itineraries` with the following structure:
- `content`: The full text of the itinerary
- `title`: The title of the itinerary
- `location`: The location of the itinerary
- `embedding`: Vector representation of the content for semantic search
- `metadata`: Additional information about the itinerary

### Sample Data
The agent initializes the index with sample itineraries for:
- Luxury Beach Vacation (Maldives)
- City Explorer Package (New York)
- Mountain Retreat (Swiss Alps)

### Models Used
- **Text Generation**: google/flan-t5-large (with fallback to google/flan-t5-base)
- **Sentence Embeddings**: all-MiniLM-L6-v2

## Error Handling
The agent includes robust error handling with graceful fallbacks:
- If Elasticsearch is unavailable, it logs the error and continues with limited functionality
- If the primary generation model fails to load, it attempts to load a smaller fallback model
- If no relevant documents are found, it generates a generic itinerary based on extracted information

## Future Improvements
- Integration with more sophisticated NER models for better location and preference extraction
- Support for multi-language queries and responses
- Personalization based on user history and preferences
- Integration with hotel booking APIs for real-time availability and pricing