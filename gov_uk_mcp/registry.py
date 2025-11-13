"""Tool registry for Gov.uk MCP Server."""
from typing import Dict, Callable, Any
from mcp.types import Tool


class ToolRegistry:
    """Central registry for MCP tools."""

    _tools: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def register(cls, name: str, description: str, input_schema: dict):
        """Decorator to register a tool.

        Args:
            name: Tool name
            description: Tool description
            input_schema: JSON schema for tool input

        Example:
            @ToolRegistry.register(
                name="check_mot",
                description="Check MOT history",
                input_schema={
                    "type": "object",
                    "properties": {"registration": {"type": "string"}},
                    "required": ["registration"]
                }
            )
            def check_mot(registration):
                ...
        """
        def decorator(func: Callable):
            cls._tools[name] = {
                "handler": func,
                "description": description,
                "input_schema": input_schema
            }
            return func
        return decorator

    @classmethod
    def get_handler(cls, name: str) -> Callable:
        """Get tool handler by name.

        Args:
            name: Tool name

        Returns:
            Tool handler function or None if not found
        """
        tool = cls._tools.get(name)
        return tool["handler"] if tool else None

    @classmethod
    def list_tools(cls) -> list[Tool]:
        """Get list of all registered tools.

        Returns:
            List of Tool objects for MCP protocol
        """
        return [
            Tool(
                name=name,
                description=info["description"],
                inputSchema=info["input_schema"]
            )
            for name, info in cls._tools.items()
        ]

    @classmethod
    def get_tool_names(cls) -> list[str]:
        """Get list of all registered tool names.

        Returns:
            List of tool names
        """
        return list(cls._tools.keys())

    @classmethod
    def clear(cls):
        """Clear all registered tools (useful for testing)."""
        cls._tools = {}
