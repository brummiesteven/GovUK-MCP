"""Tests for ToolRegistry.

This module tests the ToolRegistry registration, lookup, and listing functionality.
"""

import pytest
from tests.mock_mcp import Tool
from gov_uk_mcp.registry import ToolRegistry


class TestToolRegistry:
    """Test ToolRegistry functionality."""

    def setup_method(self):
        """Clear registry before each test."""
        ToolRegistry.clear()

    def teardown_method(self):
        """Clear registry after each test."""
        ToolRegistry.clear()

    def test_register_tool_with_decorator(self):
        """Test registering a tool using the decorator."""

        @ToolRegistry.register(
            name="test_tool",
            description="A test tool",
            input_schema={
                "type": "object",
                "properties": {"param": {"type": "string"}},
                "required": ["param"],
            },
        )
        def test_tool_handler(param: str) -> dict:
            return {"result": param}

        # Verify tool is registered
        assert "test_tool" in ToolRegistry.get_tool_names()

        # Verify handler can be retrieved
        handler = ToolRegistry.get_handler("test_tool")
        assert handler is not None
        assert handler("test_value") == {"result": "test_value"}

    def test_register_multiple_tools(self):
        """Test registering multiple tools."""

        @ToolRegistry.register(
            name="tool_one",
            description="First tool",
            input_schema={"type": "object", "properties": {}},
        )
        def tool_one() -> dict:
            return {"tool": "one"}

        @ToolRegistry.register(
            name="tool_two",
            description="Second tool",
            input_schema={"type": "object", "properties": {}},
        )
        def tool_two() -> dict:
            return {"tool": "two"}

        tool_names = ToolRegistry.get_tool_names()
        assert len(tool_names) == 2
        assert "tool_one" in tool_names
        assert "tool_two" in tool_names

    def test_get_handler_existing_tool(self):
        """Test retrieving handler for existing tool."""

        @ToolRegistry.register(
            name="existing_tool",
            description="An existing tool",
            input_schema={"type": "object", "properties": {}},
        )
        def existing_tool_handler() -> dict:
            return {"status": "success"}

        handler = ToolRegistry.get_handler("existing_tool")
        assert handler is not None
        assert callable(handler)
        assert handler() == {"status": "success"}

    def test_get_handler_nonexistent_tool(self):
        """Test retrieving handler for non-existent tool returns None."""
        handler = ToolRegistry.get_handler("nonexistent_tool")
        assert handler is None

    def test_list_tools_empty_registry(self):
        """Test listing tools when registry is empty."""
        tools = ToolRegistry.list_tools()
        assert isinstance(tools, list)
        assert len(tools) == 0

    def test_list_tools_with_registered_tools(self):
        """Test listing tools returns correct Tool objects."""

        @ToolRegistry.register(
            name="list_test_tool",
            description="A tool for list testing",
            input_schema={
                "type": "object",
                "properties": {"param": {"type": "string"}},
                "required": ["param"],
            },
        )
        def list_test_tool_handler(param: str) -> dict:
            return {"param": param}

        tools = ToolRegistry.list_tools()
        assert len(tools) == 1
        assert isinstance(tools[0], Tool)
        assert tools[0].name == "list_test_tool"
        assert tools[0].description == "A tool for list testing"
        assert tools[0].inputSchema["type"] == "object"
        assert "param" in tools[0].inputSchema["properties"]

    def test_list_tools_multiple_tools(self):
        """Test listing multiple registered tools."""

        @ToolRegistry.register(
            name="tool_alpha",
            description="Alpha tool",
            input_schema={"type": "object", "properties": {}},
        )
        def tool_alpha() -> dict:
            return {}

        @ToolRegistry.register(
            name="tool_beta",
            description="Beta tool",
            input_schema={"type": "object", "properties": {}},
        )
        def tool_beta() -> dict:
            return {}

        @ToolRegistry.register(
            name="tool_gamma",
            description="Gamma tool",
            input_schema={"type": "object", "properties": {}},
        )
        def tool_gamma() -> dict:
            return {}

        tools = ToolRegistry.list_tools()
        assert len(tools) == 3

        tool_names = [tool.name for tool in tools]
        assert "tool_alpha" in tool_names
        assert "tool_beta" in tool_names
        assert "tool_gamma" in tool_names

    def test_get_tool_names_empty_registry(self):
        """Test getting tool names when registry is empty."""
        names = ToolRegistry.get_tool_names()
        assert isinstance(names, list)
        assert len(names) == 0

    def test_get_tool_names_with_tools(self):
        """Test getting tool names returns list of strings."""

        @ToolRegistry.register(
            name="name_test_tool",
            description="Tool for name testing",
            input_schema={"type": "object", "properties": {}},
        )
        def name_test_tool_handler() -> dict:
            return {}

        names = ToolRegistry.get_tool_names()
        assert isinstance(names, list)
        assert len(names) == 1
        assert "name_test_tool" in names

    def test_clear_registry(self):
        """Test clearing the registry removes all tools."""

        @ToolRegistry.register(
            name="clear_test_tool",
            description="Tool to test clearing",
            input_schema={"type": "object", "properties": {}},
        )
        def clear_test_tool_handler() -> dict:
            return {}

        # Verify tool is registered
        assert len(ToolRegistry.get_tool_names()) == 1

        # Clear registry
        ToolRegistry.clear()

        # Verify registry is empty
        assert len(ToolRegistry.get_tool_names()) == 0
        assert len(ToolRegistry.list_tools()) == 0

    def test_register_overwrites_existing_tool(self):
        """Test that re-registering a tool overwrites the previous registration."""

        @ToolRegistry.register(
            name="overwrite_tool",
            description="Original description",
            input_schema={"type": "object", "properties": {}},
        )
        def original_handler() -> dict:
            return {"version": "original"}

        @ToolRegistry.register(
            name="overwrite_tool",
            description="New description",
            input_schema={"type": "object", "properties": {}},
        )
        def new_handler() -> dict:
            return {"version": "new"}

        # Should still have only one tool
        assert len(ToolRegistry.get_tool_names()) == 1

        # Handler should be the new one
        handler = ToolRegistry.get_handler("overwrite_tool")
        assert handler() == {"version": "new"}

        # Description should be updated
        tools = ToolRegistry.list_tools()
        assert tools[0].description == "New description"

    def test_register_preserves_function_behavior(self):
        """Test that decorator preserves original function behavior."""

        @ToolRegistry.register(
            name="preserve_test",
            description="Test preservation",
            input_schema={
                "type": "object",
                "properties": {"a": {"type": "integer"}, "b": {"type": "integer"}},
                "required": ["a", "b"],
            },
        )
        def add_numbers(a: int, b: int) -> dict:
            """Add two numbers."""
            return {"sum": a + b}

        # Function should still work when called directly
        result = add_numbers(5, 3)
        assert result == {"sum": 8}

        # Function should also work when retrieved from registry
        handler = ToolRegistry.get_handler("preserve_test")
        result = handler(10, 20)
        assert result == {"sum": 30}

    def test_register_with_complex_input_schema(self):
        """Test registering tool with complex input schema."""
        complex_schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string", "minLength": 1},
                "age": {"type": "integer", "minimum": 0},
                "email": {"type": "string", "format": "email"},
                "tags": {"type": "array", "items": {"type": "string"}},
                "metadata": {
                    "type": "object",
                    "properties": {"key": {"type": "string"}},
                },
            },
            "required": ["name", "email"],
        }

        @ToolRegistry.register(
            name="complex_tool", description="Tool with complex schema", input_schema=complex_schema
        )
        def complex_tool_handler(**kwargs) -> dict:
            return {"received": kwargs}

        tools = ToolRegistry.list_tools()
        assert len(tools) == 1
        assert tools[0].inputSchema == complex_schema

    def test_registry_isolation_between_tests(self):
        """Test that registry state is isolated between tests."""
        # This test verifies that setup_method and teardown_method work correctly
        # The registry should be empty at the start of this test
        assert len(ToolRegistry.get_tool_names()) == 0

        @ToolRegistry.register(
            name="isolation_test",
            description="Test isolation",
            input_schema={"type": "object", "properties": {}},
        )
        def isolation_test_handler() -> dict:
            return {}

        assert len(ToolRegistry.get_tool_names()) == 1

    def test_tool_with_no_parameters(self):
        """Test registering and calling tool with no parameters."""

        @ToolRegistry.register(
            name="no_params_tool",
            description="Tool with no parameters",
            input_schema={"type": "object", "properties": {}},
        )
        def no_params_handler() -> dict:
            return {"status": "success", "message": "No parameters needed"}

        handler = ToolRegistry.get_handler("no_params_tool")
        result = handler()
        assert result["status"] == "success"

    def test_tool_with_optional_parameters(self):
        """Test registering tool with optional parameters."""

        @ToolRegistry.register(
            name="optional_params_tool",
            description="Tool with optional parameters",
            input_schema={
                "type": "object",
                "properties": {
                    "required_param": {"type": "string"},
                    "optional_param": {"type": "string", "default": "default_value"},
                },
                "required": ["required_param"],
            },
        )
        def optional_params_handler(required_param: str, optional_param: str = "default_value"):
            return {"required": required_param, "optional": optional_param}

        handler = ToolRegistry.get_handler("optional_params_tool")

        # Call with only required parameter
        result = handler("test")
        assert result["required"] == "test"
        assert result["optional"] == "default_value"

        # Call with both parameters
        result = handler("test", "custom")
        assert result["required"] == "test"
        assert result["optional"] == "custom"
