Cape Town RAG Chat
==================

A chatbot that answers questions about Cape Town and the Western Cape using RAG (Retrieval Augmented Generation). Built with FastAPI, React, and OpenAI.

Developed by: Branden Reddy


What This App Does
==================

It's a chat application where you can ask questions about Cape Town tourism, attractions, wine regions, and things to do in the area. The backend pulls relevant info from a Wesgro tourism guide and feeds that context to the LLM so the answers are actually useful and grounded in real data.

Responses stream in real time so you see text appearing as it generates. You can have multiple conversations going and switch between them, everything gets saved locally.


MCP Server List
===============

The project includes a local MCP (Model Context Protocol) server with the following tools:

    Tool Name           Description                                    Endpoint
    get_current_time    Returns current date and time in SAST         POST /tools/get_current_time
    get_timezone_info   Returns South African timezone details        POST /tools/get_timezone_info

The MCP server runs on http://localhost:5001 and provides time related functionality to the chatbot.


How to Start the Backend
========================

1. Navigate to backend folder
   cd backend

2. Set up virtual environment
   python -m venv venv
   venv\Scripts\activate     (Windows)
   source venv/bin/activate  (Mac/Linux)

3. Install dependencies
   pip install -e .

4. Create a .env file with your OpenAI key
   OPENAI_API_KEY=your_key_here

5. Start the server
   uvicorn app.main:app --reload --port 8000

First run takes a bit longer because it builds the embeddings from the source data.
Backend runs on http://localhost:8000


How to Start the Frontend
=========================

1. Navigate to frontend folder
   cd frontend

2. Install packages
   npm install

3. Start dev server
   npm run dev

Frontend runs on http://localhost:5173


How to Start the MCP Server (Optional)
======================================

cd mcp_server
pip install -r requirements.txt
python server.py

MCP server runs on http://localhost:5001
The main app works without it, just falls back to local system time.


Architecture and Design Decisions
=================================

Backend: FastAPI (Python)
    Chose FastAPI over Flask because of native async support. Streaming responses work smoothly with AsyncOpenAI client and StreamingResponse. Also provides automatic API docs at /docs.

Frontend: React with Vite
    React for the interactive UI, Vite for fast development builds. Kept it simple with plain CSS styling, no UI frameworks.

LLM: OpenAI GPT-4o-mini
    Good balance of speed and quality for a chat application. Supports streaming out of the box.

Embeddings: OpenAI text-embedding-3-small
    Same provider as LLM so one API key covers everything. Accurate enough for semantic search on this dataset size.

Vector Search: NumPy cosine similarity
    For under 100 document chunks, numpy handles similarity calculation in milliseconds. A full vector database would add complexity without benefit at this scale.

Data Storage: JSON files
    Simple and works well for a demo. Each chat is its own file which makes debugging easy. For production would use PostgreSQL or MongoDB.

Streaming: Server Sent Events (SSE)
    Simpler than WebSockets for one way server to client communication. Browser handles reconnection automatically.

MCP Integration: Separate FastAPI service
    Demonstrates the concept of external tool servers. Currently provides time/date tools but architecture supports adding more.


Project Layout
==============

mini-rag-app/
    backend/
        app/
            main.py           FastAPI routes and endpoints
            chat.py           Chat logic and streaming
            rag.py            Embeddings and similarity search
            mcp_client.py     MCP server integration
        data/
            cape_town_data.txt    Source text from the PDF
            chats/                Saved conversations as JSON
            embeddings/           Cached embedding index
        pyproject.toml
        .env.example
    frontend/                 React application
    mcp_server/              Local MCP time service
    README.md
    ARCHITECTURE.md          Detailed architecture notes
    PRESENTATION.md          Presentation and Q&A prep


Features Implemented
====================

Task 0: Python environment with pyproject.toml
Task 1: Chat frontend (React) connected to backend (FastAPI) with LLM responses
Task 2: Real time streaming of responses token by token
Task 3: Multiple chats with switching and persistence
Task 3: RAG component using local documents (Cape Town tourism guide)
Task 4: Local MCP server integration (time service)


Optional Enhancements
=====================

Vector Store:
    Used simple embeddings with NumPy cosine similarity. This works well for the current dataset size. For larger datasets, would integrate FAISS or Chroma.

Docker Support:
    Not implemented in current version. To add Docker support would need:
        Dockerfile for backend (Python/FastAPI)
        Dockerfile for frontend (Node/React build)
        docker-compose.yml to orchestrate services
        Environment variable handling for API keys


API Endpoints
=============

Chat:
    POST /api/chat              Send message and get streaming response
    GET  /api/chats             List all conversations
    POST /api/chats             Create new conversation
    GET  /api/chats/{id}        Get specific conversation
    DELETE /api/chats/{id}      Delete conversation

RAG:
    GET /api/rag/search?query=  Search documents directly

MCP:
    GET  /api/mcp/tools         List available MCP tools
    POST /api/mcp/call/{tool}   Call specific MCP tool
