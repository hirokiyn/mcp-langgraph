from mcp.server.fastmcp import FastMCP

# Create a FastMCP server instance with the name "Math"
mcp = FastMCP("Math")


@mcp.tool()
def add(a: float, b: float) -> float:
    """
    Add two numbers.

    Args:
        a (float): The first number.
        b (float): The second number.

    Returns:
        float: The sum of the two numbers.
    """
    try:
        return a + b
    except Exception as e:
        return f"Error: {e}"


@mcp.tool()
def multiply(a: float, b: float) -> float:
    """
    Multiply two numbers.

    Args:
        a (float): The first number.
        b (float): The second number.

    Returns:
        float: The product of the two numbers.
    """
    try:
        return a * b
    except Exception as e:
        return f"Error: {e}"


if __name__ == "__main__":
    # Run the MCP server using the stdio transport
    mcp.run(transport="stdio")
