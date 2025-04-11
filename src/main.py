from langchain_core.messages import HumanMessage
from langchain_mcp_adapters.client import MultiServerMCPClient

from src.agent_graph import build_graph


async def stream_graph_updates(user_input: str):
    """
    Streams updates from the agent graph based on user input.

    Args:
        user_input (str): The input from the user.
    """
    async with MultiServerMCPClient(
        {
            "math": {
                "command": "python",
                "args": ["src/mcp_servers/math_server.py"],
                "transport": "stdio",
            },
            "weather": {
                # Make sure you start your weather server on port 8000
                "url": "http://localhost:8000/sse",
                "transport": "sse",
            },
        }
    ) as client:
        graph = await build_graph(client)

        async for event in graph.astream(
            {"messages": [HumanMessage(content=user_input)]}
        ):
            try:
                for value in event.values():
                    print("Assistant:", value["messages"][-1].content)
            except Exception as e:
                print(f"Error processing event: {e}")


async def agent():
    """
    An asynchronous agent that interacts with the user and streams graph updates.
    """
    while True:
        try:
            user_input = input("User: ")
            if user_input.lower() in ["quit", "exit", "q"]:
                print("Goodbye!")
                break

            await stream_graph_updates(user_input)

        except Exception as e:
            print(f"Error: {e}")
            break


def main():
    """
    Main function to run the agent.
    """
    import asyncio

    asyncio.run(agent())
