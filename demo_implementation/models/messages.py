from typing import Optional, Dict, Union, Any, List, Literal
from pydantic import BaseModel, Field, RootModel

class ConnectionResponse(BaseModel):
    event: str = Field(..., description="Event type")
    data: str = Field(..., description="Event data")

class Request(BaseModel):
    """Base class for JSON-RPC 2.0 requests"""
    jsonrpc: str = Field(default="2.0", description="JSON-RPC protocol version")
    id: Union[int, str] = Field(default=None, description="Request identifier")
    method: str = Field(..., description="Method to be invoked")
    params: Optional[Dict[str, Any]] = Field(default=None, description="Method parameters")

class Result(RootModel):
    root: Dict[str, Any] = Field(description="Method result as key-value pairs")


class Error(BaseModel):
    code: int = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    data: Optional[Any] = Field(default=None, description="Additional error data")


class Capabilities(BaseModel):
    tools: Dict = Field(default={}, description="Server capabilities")

class InitializeResult(BaseModel):
    protocolVersion: str = Field(..., description="Protocol version")
    capabilities: Capabilities = Field(..., description="Server capabilities")
    serverInfo: Dict[str, Any] = Field(..., description="Server information")

class Tool(BaseModel):
    name: str = Field(..., description="Tool name")
    description: str = Field(..., description="Tool description")
    inputSchema: Dict[str, Any] = Field(..., description="Tool input schema")

class TextItem(BaseModel):
    type: Literal["text"] = Field(..., description="Content type")
    text: str = Field(..., description="Content text")

class Response(BaseModel):
    """Base class for JSON-RPC 2.0 responses"""
    jsonrpc: str = Field(default="2.0", description="JSON-RPC protocol version")
    id: Union[int, str] = Field(default=None, description="Request identifier")
    result: Optional[Any] = Field(default=None, description="Method result")
    error: Optional[Error] = Field(default=None, description="Error information")

    def model_dump(self, **kwargs):
        kwargs.setdefault('exclude_none', True)
        return super().model_dump(**kwargs)

class Notification(BaseModel):
    """Base class for JSON-RPC 2.0 notifications (requests without an id)"""
    jsonrpc: str = Field(default="2.0", description="JSON-RPC protocol version")
    method: str = Field(..., description="Method to be invoked")
    params: Optional[Dict[str, Any]] = Field(default=None, description="Method parameters")

# Standard JSON-RPC 2.0 error codes
class ErrorCodes:
    PARSE_ERROR = -32700
    INVALID_REQUEST = -32600
    METHOD_NOT_FOUND = -32601
    INVALID_PARAMS = -32602
    INTERNAL_ERROR = -32603
    SERVER_ERROR_START = -32000
    SERVER_ERROR_END = -32099 