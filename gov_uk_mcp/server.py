"""Gov.uk MCP Server - Main server implementation."""
import asyncio
import json
import logging
from dotenv import load_dotenv

from mcp.server import Server
from mcp.types import Tool, TextContent

from gov_uk_mcp.registry import ToolRegistry
import gov_uk_mcp.tool_definitions  # noqa: F401 - Import to register tools

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

app = Server("gov-uk-mcp")


@app.list_tools()
async def list_tools() -> list[Tool]:
    """List all available tools."""
    return ToolRegistry.list_tools()


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Call a tool with the given arguments."""
    logger.info(f"Tool called: {name}")

    try:
        # Get tool handler from registry
        handler = ToolRegistry.get_handler(name)

        if not handler:
            error_response = {"error": f"Unknown tool: {name}"}
            return [TextContent(type="text", text=json.dumps(error_response, indent=2))]

        # Call tool handler with arguments (unwrapping dict to match function signatures)
        result = await asyncio.to_thread(handler, **arguments)

        return [TextContent(type="text", text=json.dumps(result, indent=2))]

    except KeyError as e:
        logger.error(f"Missing parameter for {name}: {e}")
        error_response = {
            "error": "Missing required parameter. Please check the tool documentation for required parameters."
        }
        return [TextContent(type="text", text=json.dumps(error_response, indent=2))]
    except Exception as e:
        logger.exception(f"Tool execution failed for {name}: {type(e).__name__}")
        error_response = {
            "error": "An unexpected error occurred. Please try again or contact support if the issue persists."
        }
        return [TextContent(type="text", text=json.dumps(error_response, indent=2))]


async def main():
    """Run the server with error handling."""
    from mcp.server.stdio import stdio_server

    try:
        logger.info("Starting Gov.uk MCP Server...")
        async with stdio_server() as (read_stream, write_stream):
            await app.run(
                read_stream,
                write_stream,
                app.create_initialization_options()
            )
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main())
