"""
Extensible tool registry for MCP server.

This module provides a framework for easily adding new tools to the MCP server
without modifying core server code.
"""
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass
from mcp.types import Tool


@dataclass
class ToolDefinition:
    """Definition of a tool that can be registered."""
    name: str
    description: str
    input_schema: Dict[str, Any]
    handler: Callable


class ToolRegistry:
    """Registry for managing MCP tools dynamically."""

    def __init__(self):
        self._tools: Dict[str, ToolDefinition] = {}

    def register(
        self,
        name: str,
        description: str,
        input_schema: Dict[str, Any],
        handler: Callable
    ) -> None:
        """
        Register a new tool.

        Args:
            name: Tool name (snake_case)
            description: Human-readable description
            input_schema: JSON schema for tool parameters
            handler: Async function to handle tool execution

        Example:
            registry.register(
                name="my_custom_tool",
                description="Does something custom",
                input_schema={
                    "type": "object",
                    "properties": {
                        "param1": {"type": "string"}
                    },
                    "required": ["param1"]
                },
                handler=my_custom_tool_handler
            )
        """
        self._tools[name] = ToolDefinition(
            name=name,
            description=description,
            input_schema=input_schema,
            handler=handler
        )

    def register_decorator(
        self,
        name: str,
        description: str,
        input_schema: Dict[str, Any]
    ):
        """
        Decorator for registering tools.

        Example:
            @registry.register_decorator(
                name="my_tool",
                description="My tool description",
                input_schema={"type": "object", "properties": {...}}
            )
            async def my_tool_handler(param1: str, param2: int):
                return {"result": "success"}
        """
        def decorator(handler: Callable):
            self.register(name, description, input_schema, handler)
            return handler
        return decorator

    def get_tool(self, name: str) -> Optional[ToolDefinition]:
        """Get a tool by name."""
        return self._tools.get(name)

    def get_all_tools(self) -> List[ToolDefinition]:
        """Get all registered tools."""
        return list(self._tools.values())

    def to_mcp_tools(self) -> List[Tool]:
        """Convert registered tools to MCP Tool format."""
        return [
            Tool(
                name=tool.name,
                description=tool.description,
                inputSchema=tool.input_schema
            )
            for tool in self._tools.values()
        ]

    def tool_exists(self, name: str) -> bool:
        """Check if a tool exists."""
        return name in self._tools

    async def execute_tool(self, name: str, arguments: Dict[str, Any]) -> Any:
        """
        Execute a tool by name with given arguments.

        Args:
            name: Tool name
            arguments: Tool arguments as dict

        Returns:
            Tool execution result

        Raises:
            ValueError: If tool doesn't exist
        """
        tool = self.get_tool(name)
        if not tool:
            raise ValueError(f"Unknown tool: {name}")

        # Call handler with unpacked arguments
        return await tool.handler(**arguments)


# Global registry instance
global_registry = ToolRegistry()
