"""Mock MCP types for testing without installing the mcp package."""
from typing import Any, Dict


class Tool:
    """Mock Tool class for testing."""

    def __init__(self, name: str, description: str, inputSchema: Dict[str, Any]):
        """Initialize Tool mock.

        Args:
            name: Tool name
            description: Tool description
            inputSchema: Input schema dictionary
        """
        self.name = name
        self.description = description
        self.inputSchema = inputSchema

    def __repr__(self) -> str:
        """String representation."""
        return f"Tool(name={self.name!r}, description={self.description!r})"
