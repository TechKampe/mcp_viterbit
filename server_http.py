"""
HTTP/SSE MCP Server for Viterbit API integration.

This server provides remote access to Viterbit MCP tools via HTTP and Server-Sent Events,
allowing third-party clients to connect over the network.
"""
import asyncio
import json
import logging
import os
from typing import Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, Header, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from mcp.server import Server
from mcp.types import Tool as MCPTool

from viterbit_client import ViterbitClient, ViterbitAPIError
from tools import ViterbitTools


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Request/Response Models
class ToolCallRequest(BaseModel):
    """Request model for tool calls."""
    name: str = Field(..., description="Name of the tool to call")
    arguments: Optional[dict[str, Any]] = Field(default={}, description="Tool arguments")


class ToolCallResponse(BaseModel):
    """Response model for tool calls."""
    success: bool
    result: Any
    error: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    tools_count: int


# Global state
viterbit_client: Optional[ViterbitClient] = None
viterbit_tools: Optional[ViterbitTools] = None
mcp_server: Optional[Server] = None


# Authentication
API_KEYS = set(os.getenv("MCP_API_KEYS", "").split(","))
if not API_KEYS or API_KEYS == {""}:
    logger.warning("No API keys configured. Set MCP_API_KEYS environment variable.")
    API_KEYS = set()


async def verify_api_key(x_api_key: str = Header(..., alias="X-API-Key")):
    """Verify API key from request header."""
    if not API_KEYS:
        logger.warning("API key validation skipped - no keys configured")
        return True

    if x_api_key not in API_KEYS:
        logger.warning(f"Invalid API key attempt: {x_api_key[:8]}...")
        raise HTTPException(status_code=401, detail="Invalid API key")

    return True


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for FastAPI application."""
    global viterbit_client, viterbit_tools, mcp_server

    logger.info("Initializing Viterbit MCP Server...")

    # Load environment variables
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_file):
        from dotenv import load_dotenv
        load_dotenv(env_file)
        logger.info("Loaded environment variables from .env file")

    # Check for required environment variables
    if not os.getenv("VITERBIT_API_KEY"):
        logger.error("VITERBIT_API_KEY environment variable is required")
        raise ValueError("VITERBIT_API_KEY is required")

    try:
        # Initialize Viterbit client and tools
        viterbit_client = ViterbitClient()
        viterbit_tools = ViterbitTools(viterbit_client)

        # Initialize MCP server
        mcp_server = Server("viterbit-mcp")

        logger.info(f"Server initialized with {len(viterbit_tools.get_tools())} tools")
        logger.info(f"API authentication: {'enabled' if API_KEYS else 'disabled (WARNING)'}")

        yield

    except Exception as e:
        logger.error(f"Failed to initialize server: {e}")
        raise
    finally:
        logger.info("Shutting down Viterbit MCP Server")


# Create FastAPI app
app = FastAPI(
    title="Viterbit MCP Server",
    description="HTTP/SSE MCP Server for Viterbit API integration",
    version="2.0.0",
    lifespan=lifespan
)


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("ALLOWED_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        version="2.0.0",
        tools_count=len(viterbit_tools.get_tools()) if viterbit_tools else 0
    )


@app.get("/tools", dependencies=[Depends(verify_api_key)])
async def list_tools() -> list[dict]:
    """List all available MCP tools."""
    if not viterbit_tools:
        raise HTTPException(status_code=503, detail="Server not initialized")

    tools = viterbit_tools.get_tools()
    return [
        {
            "name": tool.name,
            "description": tool.description,
            "inputSchema": tool.inputSchema
        }
        for tool in tools
    ]


@app.post("/tools/call", dependencies=[Depends(verify_api_key)])
async def call_tool(request: ToolCallRequest) -> ToolCallResponse:
    """Execute a tool call."""
    if not viterbit_tools:
        raise HTTPException(status_code=503, detail="Server not initialized")

    logger.info(f"Tool called: {request.name} with arguments: {request.arguments}")

    try:
        result = await viterbit_tools.handle_tool_call(request.name, request.arguments)
        logger.info(f"Tool {request.name} executed successfully")

        return ToolCallResponse(
            success=True,
            result=result
        )

    except Exception as e:
        logger.error(f"Error executing tool {request.name}: {e}")
        return ToolCallResponse(
            success=False,
            result=None,
            error=str(e)
        )


@app.get("/sse", dependencies=[Depends(verify_api_key)])
async def sse_endpoint(request: Request):
    """
    Server-Sent Events endpoint for streaming MCP protocol messages.
    This allows real-time bidirectional communication with MCP clients.
    """

    async def event_generator():
        """Generate SSE events."""
        try:
            # Send initial connection event
            yield f"event: connected\ndata: {json.dumps({'status': 'connected', 'version': '2.0.0'})}\n\n"

            # Send available tools
            if viterbit_tools:
                tools_data = {
                    "type": "tools",
                    "tools": [
                        {
                            "name": tool.name,
                            "description": tool.description,
                            "inputSchema": tool.inputSchema
                        }
                        for tool in viterbit_tools.get_tools()
                    ]
                }
                yield f"event: tools\ndata: {json.dumps(tools_data)}\n\n"

            # Keep connection alive
            while True:
                if await request.is_disconnected():
                    logger.info("SSE client disconnected")
                    break

                # Send keepalive every 30 seconds
                yield f"event: ping\ndata: {json.dumps({'timestamp': asyncio.get_event_loop().time()})}\n\n"
                await asyncio.sleep(30)

        except asyncio.CancelledError:
            logger.info("SSE stream cancelled")
        except Exception as e:
            logger.error(f"SSE error: {e}")
            yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Viterbit MCP Server",
        "version": "2.0.0",
        "protocol": "HTTP/SSE",
        "endpoints": {
            "health": "/health",
            "tools": "/tools",
            "call": "/tools/call",
            "sse": "/sse"
        },
        "authentication": "X-API-Key header required" if API_KEYS else "None (warning)",
        "documentation": "/docs"
    }


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8000"))
    host = os.getenv("HOST", "0.0.0.0")

    logger.info(f"Starting Viterbit MCP HTTP/SSE Server on {host}:{port}")

    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )
