# 🛫 NLP Multi-Agent Travel Chatbot

A sophisticated NLP-based multi-agent chatbot application that provides comprehensive travel assistance including flight searches, hotel bookings, and AI-powered itinerary generation using Retrieval-Augmented Generation (RAG).

## 🌟 Features

### Core Capabilities
- **✈️ Flight Agent**: Real-time flight availability using Amadeus API
- **🏨 Hotel Agent**: Hotel search and booking via Booking.com RapidAPI
- **🤖 RAG Agent**: AI-powered itinerary generation using Amazon Bedrock Titan
- **💬 Natural Language Processing**: Intent recognition and entity extraction
- **🌐 Web Interface**: Modern, responsive chatbot UI

### Advanced Features
- **Multi-Agent Architecture**: Coordinated communication between specialized agents
- **Context-Aware Responses**: Maintains conversation context across multiple turns
- **Personalized Recommendations**: Tailored suggestions based on user preferences
- **Real-Time Data Integration**: Live flight and hotel availability
- **Fallback Mechanisms**: Robust error handling and graceful degradation

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API    │    │  External APIs  │
│   (HTML/CSS/JS) │◄──►│   (FastAPI)      │◄──►│  (Amadeus,      │
│                 │    │                  │    │   Booking.com)  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  Orchestrator    │
                    │  (Intent/Entity  │
                    │   Recognition)   │
                    └──────────────────┘
                              │
                    ┌─────────┼─────────┐
                    ▼         ▼         ▼
            ┌──────────┐ ┌──────────┐ ┌──────────┐
            │  Flight  │ │  Hotel   │ │   RAG    │
            │  Agent   │ │  Agent   │ │  Agent   │
            └──────────┘ └──────────┘ └──────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  AWS Bedrock     │
                    │  (Titan LLM +    │
                    │   Embeddings)    │
                    └──────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- AWS Account with Bedrock access
- Amadeus API credentials
- Booking.com RapidAPI key

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd nlp-travel-chatbot
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp env_template.txt .env
   # Edit .env with your actual API keys
   ```

5. **Start the backend server**
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

6. **Open the frontend**
   ```bash
   # Open frontend/index.html in your browser
   # Or serve it with a local server
   python -m http.server 3000  # From frontend directory
   ```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the `backend` directory with the following variables:

```env
# Amadeus API (Flight searches)
AMADEUS_API_KEY=your_amadeus_api_key
AMADEUS_API_SECRET=your_amadeus_api_secret

# Booking.com RapidAPI (Hotel searches)
BOOKING_API_KEY=your_booking_rapidapi_key

# AWS Bedrock (RAG functionality)
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
AWS_DEFAULT_REGION=us-east-1
BEDROCK_MODEL_ID=amazon.titan-text-express-v1
```

### API Keys Setup

1. **Amadeus API**: Sign up at [Amadeus for Developers](https://developers.amadeus.com/)
2. **Booking.com RapidAPI**: Get your key from [RapidAPI Booking.com](https://rapidapi.com/booking-com/api/booking-com15/)
3. **AWS Bedrock**: Enable Bedrock in your AWS account and configure IAM permissions

## 📁 Project Structure

```
nlp-travel-chatbot/
├── backend/
│   ├── agents/
│   │   ├── flight_agent/          # Flight search functionality
│   │   ├── hotel_agent/           # Hotel search functionality
│   │   └── rag_agent/             # RAG-powered itinerary generation
│   ├── orchestrator/              # Multi-agent coordination
│   ├── main.py                    # FastAPI application
│   ├── requirements.txt           # Python dependencies
│   └── env_template.txt           # Environment variables template
├── frontend/
│   └── index.html                 # Chatbot web interface
├── .gitignore                     # Git ignore rules
└── README.md                      # This file
```

## 🎯 Usage Examples

### Flight Search
```
User: "Find flights from New York to London on 2025-06-15"
Bot: [Shows available flights with prices and details]
```

### Hotel Search
```
User: "Show me hotels in Paris for 3 nights"
Bot: [Displays hotel options with ratings and prices]
```

### Complete Itinerary
```
User: "I need a 5-day travel plan for Tokyo with flights and hotels"
Bot: [Generates comprehensive itinerary with:
      - Flight options
      - Hotel recommendations
      - Daily activities
      - Sightseeing suggestions
      - Travel tips]
```

## 🔌 API Endpoints

### Core Endpoints
- `POST /chat` - Main chat interface
- `GET /health` - Health check
- `POST /rag/integrated` - Generate complete travel itinerary

### Agent-Specific Endpoints
- `POST /flight/search` - Search flights
- `POST /hotel/search` - Search hotels
- `POST /rag/generate` - Generate itinerary

## 🛠️ Development

### Running Tests
```bash
# Test individual components
python -m pytest tests/

# Test API endpoints
python test_api_endpoints.py
```

### Adding New Agents
1. Create agent class in `backend/agents/`
2. Implement required methods
3. Register with orchestrator
4. Update API endpoints

### Customizing NLP
- Modify intent patterns in `orchestrator/chatbot_orchestrator.py`
- Add new entity extraction rules
- Update response templates

## 🚀 Deployment

### Docker Deployment
```bash
# Build image
docker build -t travel-chatbot .

# Run container
docker run -p 8000:8000 --env-file .env travel-chatbot
```

### Cloud Deployment
- **AWS**: Use ECS, Lambda, or EC2
- **Google Cloud**: App Engine or Cloud Run
- **Azure**: Container Instances or App Service

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Amadeus API](https://developers.amadeus.com/) for flight data
- [Booking.com RapidAPI](https://rapidapi.com/booking-com/api/booking-com15/) for hotel data
- [Amazon Bedrock](https://aws.amazon.com/bedrock/) for AI capabilities
- [LangChain](https://langchain.com/) for RAG implementation
- [FastAPI](https://fastapi.tiangolo.com/) for the web framework

## 📞 Support

For support, email your-email@example.com or create an issue in this repository.

---

**Happy Traveling! ✈️🏨🌍**