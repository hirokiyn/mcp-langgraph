from mcp.server.fastmcp import FastMCP

# Create a FastMCP server instance with the name "Weather"
mcp = FastMCP("Weather")


@mcp.tool()
async def get_weather(location: str) -> str:
    """
    Get weather for location.

    Args:
        location (str): The location to get the weather for.

    Returns:
        str: A string describing the weather in the given location.
    """
    try:
        return "It's always sunny in New York"
    except Exception as e:
        return f"Error: {e}"


if __name__ == "__main__":
    # Run the MCP server using the sse transport
    mcp.run(transport="sse")
