import httpx
from datetime import datetime

MCP_SERVER_URL = "http://localhost:5001"

AVAILABLE_TOOLS = [
    {
        "name": "get_current_time",
        "description": "Returns the current date and time in Cape Town"
    },
    {
        "name": "get_timezone_info",
        "description": "Returns timezone information for South Africa"
    }
]


def get_available_tools() -> list:
    return AVAILABLE_TOOLS


async def call_mcp_tool(tool_name: str, params: dict = None) -> str:
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.post(
                f"{MCP_SERVER_URL}/tools/{tool_name}",
                json=params or {}
            )

            if response.status_code == 200:
                return response.json().get("result", "")
            else:
                return None

    except httpx.ConnectError:
        if tool_name == "get_current_time":
            now = datetime.now()
            return now.strftime("%A, %d %B %Y at %H:%M:%S (SAST)")
        elif tool_name == "get_timezone_info":
            return "South Africa Standard Time (SAST), UTC+2, no daylight saving"
        return None

    except Exception as e:
        print(f"MCP error: {e}")
        return None
