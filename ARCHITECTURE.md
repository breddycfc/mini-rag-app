Architecture Notes


Notes on the design decisions and how everything fits together.


Overview

Three main pieces:

1. FastAPI backend handling chat requests, RAG lookups, and response streaming
2. React frontend with the chat interface and conversation sidebar
3. MCP server providing external tools (time/date stuff for now)


Backend


Why FastAPI?

Picked FastAPI over Flask because of the async support. When you're streaming responses and calling external APIs, async just makes life easier. Plus FastAPI plays nicely with SSE through the sse-starlette package.


How Chat Messages Flow Through


When a message comes in this is roughly what happens:

1. Message gets saved to that chat's JSON file
2. RAG search runs to find relevant passages
3. Check if the question is about time/date, call MCP if so
4. Build the system prompt with RAG context included
5. Stream the response back chunk by chunk
6. Save the full response once complete


How RAG Works


Kept it fairly simple. Source data is from the Wesgro Cape Town tourism guide.

On startup the app checks if we already have embeddings saved. If not, it:
    Splits the text into chunks of about 500 words with some overlap
    Generates embeddings using OpenAI's text-embedding-3-small
    Saves everything to a JSON file for next time

When a question comes in:
    Embed the question
    Calculate cosine similarity against all the chunks
    Return top 3 matches

These matches get added to the system prompt so the model has context to work with.

Thought about using FAISS but honestly for under 100 chunks numpy is fast enough and keeps things simple.


Storing Chats

Each chat is its own JSON file in the data/chats folder. File contains:

    Chat ID (just a UUID)
    Title (grabbed from the first message)
    Created timestamp
    Messages array with role, content, time, and any RAG sources used

JSON files work fine for a demo. Easy to inspect, easy to debug. Production app would want a proper database obviously.


Streaming Setup
Went with Server Sent Events. The flow:

1. Frontend POSTs to /api/chat
2. Backend returns an EventSourceResponse
3. As tokens come in from OpenAI we yield them as events
4. Frontend reads the stream and updates in real time

SSE made more sense than WebSockets here. Only need server to client communication, and the browser's EventSource handles reconnection for you.


Frontend

Component Structure

Three components doing most of the work:

App: Top level container, holds the state for chats and messages
ChatSidebar: The conversation list on the left side
ChatWindow: Main chat area with messages and input field

State lives in App and passes down through props. App is small enough that Redux or Context would be overkill.


Handling the Stream

Frontend uses Fetch API with ReadableStream to process the SSE response. Read chunks as they arrive, parse out the SSE format, update state with new content. Had to handle buffering carefully since chunks dont always line up with message boundaries.


Styling


Just plain CSS. Dark colour scheme. Flexbox layout with fixed width sidebar and the chat area filling the rest.


MCP Server

Separate FastAPI app on port 5001. Two tools available:

get_current_time: Formatted datetime in South African time
get_timezone_info: Timezone details

Main backend calls these over HTTP when it detects time related questions. If MCP is down it falls back to local Python datetime.

Kept it separate to demonstrate the concept of having external tool servers the model can interact with.


Limitations and Tradeoffs


No auth: Demo app, skipped it entirely. Real thing would need it.

Embeddings in memory: Fine for small data. Bigger dataset would need a proper vector store.

Basic similarity: Just cosine similarity, no reranking or anything clever.

No summarization: Long chats could hit context limits eventually.

Minimal error handling: Happy path works, edge cases might be rough.


Given More Time

Would probably, not limited:
    Try sentence based chunking instead of word count
    Auto generate better chat titles from the conversation
    Add proper loading and error states in the UI
    Let users upload their own documents
    Add some rate limiting
    Write actual tests
