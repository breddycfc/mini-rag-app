from fastapi import FastAPI
from datetime import datetime
import pytz

app = FastAPI(title="Cape Town MCP Server")

CAPE_TOWN_TZ = pytz.timezone("Africa/Johannesburg")


@app.get("/")
async def root():
    return {
        "name": "Cape Town MCP Server",
        "version": "1.0.0",
        "tools": ["get_current_time", "get_timezone_info"]
    }


@app.get("/tools")
async def list_tools():
    return {
        "tools": [
            {
                "name": "get_current_time",
                "description": "Returns the current date and time in Cape Town",
                "parameters": {}
            },
            {
                "name": "get_timezone_info",
                "description": "Returns timezone information for South Africa",
                "parameters": {}
            }
        ]
    }


@app.post("/tools/get_current_time")
async def get_current_time():
    now = datetime.now(CAPE_TOWN_TZ)
    return {
        "result": now.strftime("%A, %d %B %Y at %H:%M:%S (SAST)"),
        "iso": now.isoformat(),
        "timezone": "Africa/Johannesburg"
    }


@app.post("/tools/get_timezone_info")
async def get_timezone_info():
    return {
        "result": "South Africa Standard Time (SAST), UTC+2, no daylight saving time observed",
        "offset": "+02:00",
        "abbreviation": "SAST"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5001)
