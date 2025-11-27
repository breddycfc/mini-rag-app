Presentation Notes: Cape Town RAG Chat Application


What I Built


A full stack chatbot application that answers questions about Cape Town and the Western Cape. The app uses RAG (Retrieval Augmented Generation) to pull relevant info from a tourism guide before generating responses, making the answers more accurate and grounded in real data.

https://www.wesgro.co.za/uploads/files/YOUR-GUIDE-TO-CAPE-TOWN-AND-THE-WESTERN-CAPE.pdf

Key features:
    Real time streaming responses (text appears word by word like ChatGPT)
    Multiple chat conversations with history
    RAG system showing source documents and similarity scores
    MCP server integration for time/date queries
    Clean dark themed UI


Technology Stack and Why I Chose Each


Backend: FastAPI (Python)
    Why: FastAPI handles async operations really well which is crucial for streaming. It also has built in support for Server Sent Events through StreamingResponse. Flask would have worked but async with Flask is messier. FastAPI also gives us automatic API documentation at /docs which is handy for testing.

Frontend: React with Vite
    Why: React is the industry standard for building interactive UIs. Vite over Create React App because its faster to start and the hot reload is instant. For a project this size I didnt need Next.js or anything heavier.

LLM: OpenAI GPT-4o-mini
    Why: Good balance of quality and cost. Fast enough for real time streaming. The API is well documented and the Python SDK handles streaming nicely.

Embeddings: OpenAI text-embedding-3-small
    Why: Same provider as the LLM so one API key handles everything. The small model is plenty accurate for semantic search and cheaper than ada-002.

Vector Search: NumPy cosine similarity
    Why: The dataset is small (under 100 chunks) so a full vector database like FAISS or Chroma would be overkill. NumPy handles the similarity calculation in milliseconds. For a production app with thousands of documents id switch to FAISS or Pinecone.

Data Storage: JSON files
    Why: Simple and works. Each chat is its own JSON file which makes debugging easy since you can just open the file and see whats in it. Embeddings are also stored as JSON. For production youd want PostgreSQL or MongoDB but for a demo JSON keeps dependencies minimal.

Streaming: Server Sent Events (SSE)
    Why: Simpler than WebSockets for this use case. We only need one way communication (server to client). The browser handles reconnection automatically and the implementation is straightforward.


My Development Process


Step 1: Project Setup
    Created the folder structure separating backend, frontend, and MCP server
    Set up pyproject.toml for Python dependency management
    Initialized React app with Vite

Step 2: Data Preparation
    Downloaded the Wesgro Cape Town tourism guide PDF
    Extracted the text content using PyPDF2
    Saved as a plain text file for processing

Step 3: RAG System
    Built the text chunking function (500 words per chunk with overlap)
    Implemented embedding generation using OpenAI API
    Created the similarity search using cosine similarity
    Added caching so embeddings only generate once

Step 4: Backend API
    Set up FastAPI with CORS for frontend communication
    Created endpoints for chat CRUD operations
    Implemented the streaming chat endpoint using SSE
    Integrated RAG search into the chat flow

Step 5: Frontend
    Built the component structure (App, ChatSidebar, ChatWindow)
    Implemented SSE stream reading with proper buffering
    Added state management for chats and messages
    Styled with plain CSS (dark theme)

Step 6: MCP Server
    Created separate FastAPI app for MCP tools
    Implemented time/date tools for Cape Town timezone
    Integrated MCP calls into the main chat flow

Step 7: Testing and Refinement
    Tested all features end to end
    Fixed streaming issues (had to switch to AsyncOpenAI)
    Refined the UI and added loading states


Where Data is Stored
====================

Chat Conversations:
    Location: backend/data/chats/
    Format: JSON files, one per conversation
    Naming: UUID based (e.g., 550e8400-e29b-41d4-a716-446655440000.json)
    Contents: chat ID, title, timestamp, array of messages with role/content/time

Embeddings Index:
    Location: backend/data/embeddings/index.json
    Format: Single JSON file
    Contents: Array of text chunks and their corresponding embedding vectors
    Size: About 2MB for the Cape Town guide

Source Documents:
    Location: backend/data/cape_town_data.txt
    Format: Plain text extracted from PDF


Why Not a Traditional Database?


For this demo, JSON files made sense because:

    No setup required (no Docker, no database server)
    Easy to inspect and debug
    Portable (just copy the folder)
    Fast enough for single user demo

For production I would use:
    PostgreSQL with pgvector extension for embeddings
    Or MongoDB for document storage
    Redis for caching frequently accessed data


Where I Used AI Assistance


I used AI tools to help with specific technical challenges:

1. SSE Streaming Pattern
   The async generator pattern for streaming responses was something I hadnt done before. AI helped me understand how to yield events properly and handle the buffering on the frontend.

2. Cosine Similarity Implementation
   The numpy calculation for comparing embeddings. I understood the concept but AI helped with the actual matrix operations.

3. CORS Configuration
   Getting the right headers for cross origin streaming requests.

4. OpenAI API Integration
   Specifically the async client setup and streaming iteration.

What I did myself (tbh not all by myself but mostly):
    Overall architecture and design decisions
    Component structure and state management
    File based storage system
    Error handling and edge cases
    UI design and styling
    MCP server implementation




Code Walkthrough


Backend Structure:

main.py
    Entry point for the FastAPI app
    Defines all API endpoints
    Handles CORS and routing
    The /api/chat endpoint creates the streaming response

chat.py
    Contains the stream_chat_response async generator
    Builds the system prompt with RAG context
    Calls OpenAI API with streaming enabled
    Saves messages to JSON files

rag.py
    init_rag() loads or creates embeddings on startup
    chunk_text() splits documents into searchable pieces
    get_embedding() calls OpenAI embedding API
    search_documents() finds relevant chunks by similarity

mcp_client.py
    Connects to the MCP server
    Provides get_current_time and timezone tools
    Falls back to local time if server unavailable


Frontend Structure:

App.jsx
    Main component holding all state
    fetchChats() gets list of conversations
    sendMessage() handles streaming response
    Passes state down to child components

ChatSidebar.jsx
    Displays list of previous chats
    New chat button
    Delete functionality

ChatWindow.jsx
    Message display area (scrollable)
    Input form with send button
    Shows RAG sources under assistant messages


Running Locally


Terminal 1 (Backend):
    cd backend
    pip install -e .
    uvicorn app.main:app --reload --port 8000

Terminal 2 (Frontend):
    cd frontend
    npm install
    npm run dev

Terminal 3 (MCP Server, optional):
    cd mcp_server
    pip install -r requirements.txt
    python server.py

Then open http://localhost:5173





This project demonstrates a working full stack AI application with:
    Clean separation between frontend and backend
    Real time streaming for good UX
    RAG for grounded, accurate responses
    Extensibility through MCP tools
    Simple but effective data storage

The code is intentionally kept minimal and readable. In production there would be more error handling, logging, tests, and security measures. But for demonstrating the core concepts, this implementation covers all the requirements.
