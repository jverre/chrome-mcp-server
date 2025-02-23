from fastapi import HTTPException
import asyncio
import uuid
import logging
from typing import Dict
from . import messages
from ..handlers import initialization, tools, error
LOGGER = logging.getLogger(__name__)

class Session:
    def __init__(self, endpoint: str):
        self.endpoint = endpoint
        self.session_id = uuid.uuid4()
        self.initialized = False
        self.write_stream: asyncio.Queue[messages.Response] = asyncio.Queue()
        self.is_closing = False
        
        # Create and send the session URI
        session_uri = f"{self.endpoint.rstrip('/')}/message?session_id={self.session_id.hex}"
        asyncio.create_task(self.write_stream.put(
            messages.ConnectionResponse(
                event="endpoint",
                data=session_uri
            )
        ))

    async def close(self):
        """Close the session and cleanup resources"""
        if self.is_closing:
            return
            
        self.is_closing = True
        LOGGER.info(f"Closing session {self.session_id}")
        
        # Send close event to client
        await self.write_stream.put(
            messages.ConnectionResponse(
                event="close",
                data="Server shutting down"
            )
        )
        
        # Signal the event stream to close
        await self.write_stream.put(None)
        
        # Clear any pending messages
        try:
            while True:
                self.write_stream.get_nowait()
        except asyncio.QueueEmpty:
            pass
            
        LOGGER.info(f"Session {self.session_id} closed successfully")

    async def process_message(self, raw_message: Dict):
        """Process an incoming message directly"""
        message = messages.Request(**raw_message)
        LOGGER.info(f"Processing message: {message}")

        try:
            # Check initialization
            if not self.initialized and message.method not in ["initialize", "notifications/initialized"]:
                await self.write_stream.put(
                    initialization.create_initialization_error(message)
                )
                return

            if message.method == "initialize":
                await self.write_stream.put(
                    initialization.create_initialization_response(message)
                )
                return
            
            elif message.method == "notifications/initialized":
                self.initialized = True
                return
            
            elif message.method == "ping":
                await self.write_stream.put(
                    messages.Response(
                        id=message.id,
                        result={}
                    )
                )
            
            elif message.method == "tools/list":
                await self.write_stream.put(
                    tools.create_tools_list_response(message)
                )
            elif message.method == "tools/call":
                LOGGER.info(f"Processing tool call: {message}")
                tool_response = await tools.create_tool_response(message)
                await self.write_stream.put(
                    tool_response
                )
        
        except Exception as e:
            LOGGER.error(f"Error processing message: {e}")
            await self.write_stream.put(
                error.create_error_response(
                    message,
                    messages.ErrorCodes.INTERNAL_ERROR,
                    str(e)
                )
            )