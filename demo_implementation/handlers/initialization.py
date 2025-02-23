import asyncio
from ..models import messages

def create_initialization_error(message: messages.Request) -> messages.Response:
    return messages.Response(
        id=message.id,
        error=messages.Error(
            code=messages.ErrorCodes.INVALID_REQUEST,
            message="Session not initialized"
        )
    )

def create_initialization_response(message: messages.Request) -> messages.Response:
    return messages.Response(
        id=message.id,
        result={
            "protocolVersion": "2024-11-05",
            "capabilities": {"tools": {}},
            "serverInfo": {
                "name": "chrome-mcp-server",
                "version": "1.0.0"
            }
        }
    )