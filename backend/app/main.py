"""
Main FastAPI application for the Cape Town RAG Chat.
Used AI assistance for: setting up the SSE streaming pattern and CORS config.
The rest was manual implementation based on FastAPI docs.
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import json
import os
import uuid
from datetime import datetime
import asyncio

from app.chat import stream_chat_response, get_chat_history, save_message
from app.rag import search_documents, init_rag
from app.mcp_client import call_mcp_tool, get_available_tools

app = FastAPI(title="Cape Town RAG Chat")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CHATS_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "chats")
os.makedirs(CHATS_DIR, exist_ok=True)


class ChatMessage(BaseModel):
    message: str
    chat_id: Optional[str] = None


class NewChatRequest(BaseModel):
    title: Optional[str] = None


@app.on_event("startup")
async def startup():
    init_rag()


@app.get("/api/chats")
async def list_chats():
    chats = []
    if os.path.exists(CHATS_DIR):
        for filename in os.listdir(CHATS_DIR):
            if filename.endswith(".json"):
                filepath = os.path.join(CHATS_DIR, filename)
                with open(filepath, "r") as f:
                    chat_data = json.load(f)
                    chats.append({
                        "id": chat_data["id"],
                        "title": chat_data.get("title", "New Chat"),
                        "created_at": chat_data.get("created_at"),
                        "message_count": len(chat_data.get("messages", []))
                    })

    chats.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    return {"chats": chats}


@app.post("/api/chats")
async def create_chat(request: NewChatRequest):
    chat_id = str(uuid.uuid4())
    chat_data = {
        "id": chat_id,
        "title": request.title or "New Chat",
        "created_at": datetime.now().isoformat(),
        "messages": []
    }

    filepath = os.path.join(CHATS_DIR, f"{chat_id}.json")
    with open(filepath, "w") as f:
        json.dump(chat_data, f)

    return chat_data


@app.get("/api/chats/{chat_id}")
async def get_chat(chat_id: str):
    filepath = os.path.join(CHATS_DIR, f"{chat_id}.json")
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Chat not found")

    with open(filepath, "r") as f:
        return json.load(f)


@app.delete("/api/chats/{chat_id}")
async def delete_chat(chat_id: str):
    filepath = os.path.join(CHATS_DIR, f"{chat_id}.json")
    if os.path.exists(filepath):
        os.remove(filepath)
        return {"status": "deleted"}
    raise HTTPException(status_code=404, detail="Chat not found")


@app.post("/api/chat")
async def chat_endpoint(request: ChatMessage):
    chat_id = request.chat_id

    if not chat_id:
        chat_id = str(uuid.uuid4())
        chat_data = {
            "id": chat_id,
            "title": request.message[:50] + "..." if len(request.message) > 50 else request.message,
            "created_at": datetime.now().isoformat(),
            "messages": []
        }
        filepath = os.path.join(CHATS_DIR, f"{chat_id}.json")
        with open(filepath, "w") as f:
            json.dump(chat_data, f)

    save_message(chat_id, "user", request.message)

    rag_results = search_documents(request.message)

    history = get_chat_history(chat_id)

    mcp_tools = get_available_tools()

    async def generate():
        async for event in stream_chat_response(
            message=request.message,
            chat_id=chat_id,
            history=history,
            rag_context=rag_results,
            mcp_tools=mcp_tools
        ):
            data = event.get("data", "")
            yield f"data: {data}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@app.get("/api/rag/search")
async def search_rag(query: str):
    results = search_documents(query)
    return {"results": results}


@app.get("/api/mcp/tools")
async def list_mcp_tools():
    tools = get_available_tools()
    return {"tools": tools}


@app.post("/api/mcp/call/{tool_name}")
async def call_mcp(tool_name: str):
    result = await call_mcp_tool(tool_name)
    return {"result": result}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
