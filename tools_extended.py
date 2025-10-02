"""
Extended tools system - demonstrates how to add new tools easily.

This file shows how to add custom tools to the MCP server without
modifying the core tools.py file.
"""
from tool_registry import global_registry
from viterbit_client import ViterbitClient


def register_extended_tools(client: ViterbitClient):
    """
    Register additional custom tools.

    Add your new tools here following the examples below.
    """

    # Example 1: Simple tool with decorator
    @global_registry.register_decorator(
        name="ping",
        description="Simple health check tool that returns pong",
        input_schema={
            "type": "object",
            "properties": {},
            "required": []
        }
    )
    async def ping_handler():
        return {"status": "pong", "message": "Server is alive"}

    # Example 2: Tool with parameters
    @global_registry.register_decorator(
        name="echo",
        description="Echo back the provided message",
        input_schema={
            "type": "object",
            "properties": {
                "message": {
                    "type": "string",
                    "description": "Message to echo back"
                }
            },
            "required": ["message"]
        }
    )
    async def echo_handler(message: str):
        return {"echo": message, "length": len(message)}

    # Example 3: Tool using the Viterbit client
    @global_registry.register_decorator(
        name="get_candidate_summary",
        description="Get a summary of candidate information with key metrics",
        input_schema={
            "type": "object",
            "properties": {
                "email": {
                    "type": "string",
                    "description": "Candidate email address"
                }
            },
            "required": ["email"]
        }
    )
    async def get_candidate_summary_handler(email: str):
        """Get candidate summary with applications count."""
        # Get candidate details
        candidate = await client.search_candidate_by_email(email)
        if not candidate:
            return {"error": "Candidate not found"}

        candidate_id = candidate.get("id")
        details = await client.get_candidate_details(candidate_id)

        # Get active candidatures
        candidatures = await client.find_active_candidatures_by_email(email)

        return {
            "name": candidate.get("name"),
            "email": email,
            "phone": candidate.get("phone"),
            "active_applications": len(candidatures),
            "location": details.get("address", {}).get("city"),
            "profile_complete": bool(details.get("phone") and details.get("address"))
        }

    # Add more custom tools here...
    # Just copy the decorator pattern above!


# Template for adding new tools:
"""
@global_registry.register_decorator(
    name="your_tool_name",
    description="What your tool does",
    input_schema={
        "type": "object",
        "properties": {
            "param_name": {
                "type": "string",  # or "number", "boolean", "object", "array"
                "description": "Parameter description"
            }
        },
        "required": ["param_name"]  # List required parameters
    }
)
async def your_tool_handler(param_name: str):
    # Your tool logic here
    result = do_something(param_name)
    return {"result": result}
"""
