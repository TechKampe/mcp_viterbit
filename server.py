"""
MCP Server for Viterbit API integration.

This server provides MCP tools for interacting with the Viterbit recruitment API,
allowing Claude to perform candidate management, job operations, and other recruitment tasks.
"""
import asyncio
import logging
import os
from typing import Any, Sequence

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool as MCPTool

from viterbit_client import ViterbitClient, ViterbitAPIError
from tools import ViterbitTools


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ViterbitMCPServer:
    """MCP Server for Viterbit API operations."""

    def __init__(self):
        """Initialize the Viterbit MCP server."""
        self.server = Server("viterbit-mcp")
        self.client: ViterbitClient = None
        self.viterbit_tools: ViterbitTools = None

    async def setup(self):
        """Set up the server with tools and handlers."""
        try:
            # Initialize Viterbit client
            self.client = ViterbitClient()
            self.viterbit_tools = ViterbitTools(self.client)

            # Register handlers
            await self._register_handlers()

            logger.info("Viterbit MCP Server initialized successfully")

        except ViterbitAPIError as e:
            logger.error(f"Failed to initialize Viterbit client: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to initialize server: {e}")
            raise

    async def _register_handlers(self):
        """Register MCP handlers for tools and resources."""

        @self.server.list_tools()
        async def list_tools() -> list[MCPTool]:
            """List available tools."""
            return self.viterbit_tools.get_tools()

        @self.server.call_tool()
        async def call_tool(name: str, arguments: dict[str, Any] | None) -> Sequence[Any]:
            """Handle tool calls."""
            if arguments is None:
                arguments = {}

            logger.info(f"Tool called: {name} with arguments: {arguments}")

            try:
                result = await self.viterbit_tools.handle_tool_call(name, arguments)
                logger.info(f"Tool {name} executed successfully")
                return result
            except Exception as e:
                logger.error(f"Error executing tool {name}: {e}")
                raise

    async def run(self):
        """Run the MCP server."""
        try:
            await self.setup()
            logger.info("Starting Viterbit MCP Server...")

            async with stdio_server() as streams:
                await self.server.run(
                    streams[0], streams[1],
                    self.server.create_initialization_options()
                )

        except KeyboardInterrupt:
            logger.info("Server interrupted by user")
        except Exception as e:
            logger.error(f"Server error: {e}")
            raise


async def main():
    """Main entry point for the MCP server."""
    # Load environment variables from .env file if it exists
    env_file = os.path.join(os.path.dirname(__file__), '.env')
    if os.path.exists(env_file):
        from dotenv import load_dotenv
        load_dotenv(env_file)
        logger.info("Loaded environment variables from .env file")

    # Check for required environment variables
    if not os.getenv("VITERBIT_API_KEY"):
        logger.error("VITERBIT_API_KEY environment variable is required")
        print("Error: VITERBIT_API_KEY environment variable is required")
        print("Please set it in your environment or create a .env file")
        return

    # Create and run server
    server = ViterbitMCPServer()
    await server.run()


if __name__ == "__main__":
    asyncio.run(main())