<p align="center">
  <h1 align="center">NLP MULTI-AGENT TRAVEL CHATBOT</h1>
</p>

<p align="center">
  <em>Intelligent Travel Planning, Powered by Multi-Agent AI</em>
</p>

<p align="center">
  <img src="https://img.shields.io/github/last-commit/1234620/Travel-Based-Chatbot?style=flat-square&logo=git&logoColor=white&color=0080ff" alt="last-commit">
  <img src="https://img.shields.io/github/languages/top/1234620/Travel-Based-Chatbot?style=flat-square&color=0080ff" alt="top-language">
  <img src="https://img.shields.io/github/languages/count/1234620/Travel-Based-Chatbot?style=flat-square&color=0080ff" alt="languages-count">
</p>

<p align="center">
  <em>Built with the tools and technologies:</em>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB.svg?style=flat-square&logo=Python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-009688.svg?style=flat-square&logo=FastAPI&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/Next.js-000000.svg?style=flat-square&logo=nextdotjs&logoColor=white" alt="Next.js">
  <img src="https://img.shields.io/badge/React-61DAFB.svg?style=flat-square&logo=React&logoColor=black" alt="React">
  <img src="https://img.shields.io/badge/TypeScript-3178C6.svg?style=flat-square&logo=TypeScript&logoColor=white" alt="TypeScript">
  <img src="https://img.shields.io/badge/Tailwind_CSS-06B6D4.svg?style=flat-square&logo=tailwindcss&logoColor=white" alt="TailwindCSS">
  <br>
  <img src="https://img.shields.io/badge/LangChain-1C3C3C.svg?style=flat-square&logo=LangChain&logoColor=white" alt="LangChain">
  <img src="https://img.shields.io/badge/Amazon_AWS-232F3E.svg?style=flat-square&logo=amazonaws&logoColor=white" alt="AWS">
  <img src="https://img.shields.io/badge/OpenAI-412991.svg?style=flat-square&logo=OpenAI&logoColor=white" alt="OpenAI">
  <img src="https://img.shields.io/badge/Google_Gemini-8E75B2.svg?style=flat-square&logo=googlegemini&logoColor=white" alt="Google Gemini">
  <img src="https://img.shields.io/badge/FAISS-0467DF.svg?style=flat-square&logo=Meta&logoColor=white" alt="FAISS">
</p>

<br>

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [API Endpoints](#api-endpoints)
- [Usage Examples](#usage-examples)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)

---

## Overview

A sophisticated NLP-based multi-agent chatbot application that provides comprehensive travel assistance including flight searches, hotel bookings, and AI-powered itinerary generation using Retrieval-Augmented Generation (RAG).

---

## Features

### Core Capabilities
| Feature | Description |
|---|---|
| **Flight Agent** | Real-time flight availability using Amadeus API |
| **Hotel Agent** | Hotel search and booking via Booking.com RapidAPI |
| **RAG Agent** | AI-powered itinerary generation using Amazon Bedrock Titan |
| **NLP Processing** | Intent recognition and entity extraction |
| **Web Interface** | Modern, responsive chatbot UI built with Next.js |

### Advanced Features
- **Multi-Agent Architecture** — Coordinated communication between specialized agents
- **Context-Aware Responses** — Maintains conversation context across multiple turns
- **Personalized Recommendations** — Tailored suggestions based on user preferences
- **Real-Time Data Integration** — Live flight and hotel availability
- **Fallback Mechanisms** — Robust error handling and graceful degradation

---

## Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend API    │    │  External APIs  │
│   (Next.js)     │◄──►│   (FastAPI)      │◄──►│  (Amadeus,      │
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

---

## Project Structure

```
Travel-Based-Chatbot/
├── backend/
│   ├── agents/
│   │   ├── flight_agent/          # Flight search functionality
│   │   ├── hotel_agent/           # Hotel search functionality
│   │   └── rag_agent/             # RAG-powered itinerary generation
│   ├── orchestrator/              # Multi-agent coordination
│   ├── main.py                    # FastAPI application entry point
│   ├── requirements.txt           # Python dependencies
│   └── env_template.txt           # Environment variables template
├── frontend/
│   ├── app/                       # Next.js application routes
│   ├── components/                # Reusable UI components
│   ├── hooks/                     # Custom React hooks
│   ├── styles/                    # Global styles
│   └── package.json               # Node.js dependencies
├── start_app.py                   # Unified application launcher
├── .env.example                   # Environment config template
└── README.md
```

---

## Getting Started

### Prerequisites

| Requirement | Details |
|---|---|
| **Python** | 3.8+ |
| **Node.js** | 18+ |
| **AWS Account** | With Bedrock access enabled |
| **Amadeus API** | Developer credentials |
| **Booking.com API** | RapidAPI key |

### Installation

**1. Clone the repository**
```bash
git clone https://github.com/1234620/Travel-Based-Chatbot.git
cd Travel-Based-Chatbot
```

**2. Set up the backend**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
cd backend
pip install -r requirements.txt
```

**3. Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your actual API keys
```

**4. Set up the frontend**
```bash
cd frontend
npm install
```

**5. Start the application**
```bash
# Option 1: Use the unified launcher
python start_app.py

# Option 2: Start individually
# Terminal 1 - Backend
cd backend && uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2 - Frontend
cd frontend && npm run dev
```

### Environment Variables

Create a `.env` file in the `backend` directory:

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

| Service | Registration |
|---|---|
| **Amadeus API** | [Amadeus for Developers](https://developers.amadeus.com/) |
| **Booking.com API** | [RapidAPI Booking.com](https://rapidapi.com/booking-com/api/booking-com15/) |
| **AWS Bedrock** | Enable Bedrock in your AWS account and configure IAM permissions |

---

## API Endpoints

### Core Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/chat` | Main chat interface |
| `GET` | `/health` | Health check |
| `POST` | `/rag/integrated` | Generate complete travel itinerary |

### Agent-Specific Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/flight/search` | Search flights |
| `POST` | `/hotel/search` | Search hotels |
| `POST` | `/rag/generate` | Generate itinerary |

---

## Usage Examples

### Flight Search
```
User: "Find flights from New York to London on 2025-06-15"
Bot:  [Shows available flights with prices and details]
```

### Hotel Search
```
User: "Show me hotels in Paris for 3 nights"
Bot:  [Displays hotel options with ratings and prices]
```

### Complete Itinerary
```
User: "I need a 5-day travel plan for Tokyo with flights and hotels"
Bot:  [Generates comprehensive itinerary with:
      - Flight options
      - Hotel recommendations
      - Daily activities
      - Sightseeing suggestions
      - Travel tips]
```

---

## Deployment

### Docker

```bash
# Build image
docker build -t travel-chatbot .

# Run container
docker run -p 8000:8000 --env-file .env travel-chatbot
```

### Cloud Platforms

| Platform | Services |
|---|---|
| **AWS** | ECS, Lambda, or EC2 |
| **Google Cloud** | App Engine or Cloud Run |
| **Azure** | Container Instances or App Service |

---

## Development

### Running Tests
```bash
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

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- [Amadeus API](https://developers.amadeus.com/) — Flight data
- [Booking.com RapidAPI](https://rapidapi.com/booking-com/api/booking-com15/) — Hotel data
- [Amazon Bedrock](https://aws.amazon.com/bedrock/) — AI capabilities
- [LangChain](https://langchain.com/) — RAG implementation
- [FastAPI](https://fastapi.tiangolo.com/) — Backend framework
- [Next.js](https://nextjs.org/) — Frontend framework

---

<p align="center">
  For support, email <a href="mailto:amoosani123@gmail.com">amoosani123@gmail.com</a> or create an issue in this repository.
</p>
