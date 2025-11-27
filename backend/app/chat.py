"""
Chat handling and OpenAI streaming logic.
AI assisted with: async generator pattern for streaming, OpenAI API integration.
Wrote the message persistence and history management myself.
"""
import os
import json
import asyncio
from openai import AsyncOpenAI
from dotenv import load_dotenv
from datetime import datetime
from app.mcp_client import call_mcp_tool

load_dotenv()

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

CHATS_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "chats")


def get_chat_history(chat_id: str) -> list:
    filepath = os.path.join(CHATS_DIR, f"{chat_id}.json")
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            data = json.load(f)
            return data.get("messages", [])
    return []


def save_message(chat_id: str, role: str, content: str, rag_sources: list = None):
    filepath = os.path.join(CHATS_DIR, f"{chat_id}.json")

    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            chat_data = json.load(f)
    else:
        chat_data = {
            "id": chat_id,
            "title": "New Chat",
            "created_at": datetime.now().isoformat(),
            "messages": []
        }

    message = {
        "role": role,
        "content": content,
        "timestamp": datetime.now().isoformat()
    }

    if rag_sources:
        message["rag_sources"] = rag_sources

    chat_data["messages"].append(message)

    with open(filepath, "w") as f:
        json.dump(chat_data, f, indent=2)


def build_system_prompt(rag_context: list, mcp_tools: list) -> str:
    prompt = """You are a helpful assistant that specializes in Cape Town and the Western Cape region of South Africa.
You have access to a knowledge base about tourism, attractions, restaurants, wine regions, and local experiences.

Use the provided context to answer questions accurately. If the context doesn't contain relevant information,
you can still help but mention that you're drawing from general knowledge.

Be friendly and conversational, like a local guide sharing their knowledge about the area."""

    if rag_context:
        prompt += "\n\nRelevant context from the knowledge base:\n"
        for i, ctx in enumerate(rag_context, 1):
            prompt += f"\n[Source {i}] (similarity: {ctx['score']:.2f}):\n{ctx['text']}\n"

    if mcp_tools:
        prompt += "\n\nYou also have access to these tools:\n"
        for tool in mcp_tools:
            prompt += f"- {tool['name']}: {tool['description']}\n"
        prompt += "\nIf the user asks for current time or date, use the information provided."

    return prompt


async def stream_chat_response(message: str, chat_id: str, history: list, rag_context: list, mcp_tools: list):
    messages = [{"role": "system", "content": build_system_prompt(rag_context, mcp_tools)}]

    for msg in history[-10:]:
        messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })

    needs_time = any(word in message.lower() for word in ["time", "date", "today", "now", "what day"])
    time_info = None

    if needs_time and mcp_tools:
        try:
            time_info = await call_mcp_tool("get_current_time")
            if time_info:
                messages.append({
                    "role": "system",
                    "content": f"Current time information: {time_info}"
                })
        except Exception as e:
            print(f"MCP call failed: {e}")

    messages.append({"role": "user", "content": message})

    rag_data = None
    if rag_context:
        rag_data = [{"text": r["text"][:200], "score": r["score"]} for r in rag_context]

    yield {
        "event": "rag_results",
        "data": json.dumps({"sources": rag_data or []})
    }

    if time_info:
        yield {
            "event": "mcp_result",
            "data": json.dumps({"tool": "get_current_time", "result": time_info})
        }

    try:
        response = await client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            stream=True,
            temperature=0.7,
            max_tokens=1024
        )

        full_response = ""

        async for chunk in response:
            if chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
                full_response += content
                yield {
                    "event": "message",
                    "data": json.dumps({"content": content})
                }

        save_message(chat_id, "assistant", full_response, rag_data)

        yield {
            "event": "done",
            "data": json.dumps({"chat_id": chat_id})
        }

    except Exception as e:
        yield {
            "event": "error",
            "data": json.dumps({"error": str(e)})
        }
