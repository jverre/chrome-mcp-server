from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from .models import messages
from .models.session import Session
import asyncio
import json
from typing import Dict
import uuid
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # This will output to console/stdout
    ]
)

LOGGER = logging.getLogger(__name__)

app = FastAPI(title="Chrome MCP Server")

# Add CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

sessions: Dict[str, Session] = {}

@app.get("/sse")
async def events(request: Request):
    """SSE endpoint that sends periodic heartbeat messages"""
    # Create a new session
    session = Session(str(request.base_url))
    sessions[session.session_id] = session
    
    async def event_generator():
        try:
            while True:
                message = await session.write_stream.get()
                if message is None:  # Connection close signal
                    break

                if isinstance(message, messages.ConnectionResponse):
                    yield f"event: {message.event}\ndata: {message.data}\n\n"
                elif isinstance(message, messages.Response):
                    yield f"event: message\ndata: {json.dumps(message.model_dump())}\n\n"
        except asyncio.CancelledError:
            pass  # Client disconnected
        finally:
            # Cleanup
            if session.session_id in sessions:
                del sessions[session.session_id]

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
        },
        status_code=200
    )

@app.post("/message")
async def message(session_id: str, request: Request):
    """Endpoint to send a message to the session"""
    data = await request.json()
    session_id = uuid.UUID(session_id)
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    await sessions[session_id].process_message(data)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"status": "running"}
