import json
from typing import Annotated
from typing_extensions import TypedDict

from langchain_core.messages import ToolMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages


from src.common import get_llm


class State(TypedDict):
    """
    Represents the state of the agent graph.

    Attributes:
        messages (Annotated[list, add_messages]): A list of messages, which are updated by appending new messages.
    """

    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]


class BasicToolNode:
    """A node that runs the tools requested in the last AIMessage."""

    def __init__(self, tools: list) -> None:
        """
        Initializes the BasicToolNode with a list of tools.

        Args:
            tools (list): A list of tools available to the agent.
        """
        self.tools_by_name = {tool.name: tool for tool in tools}

    async def __call__(self, inputs: dict):
        """
        Executes the tools requested in the last AIMessage.

        Args:
            inputs (dict): A dictionary containing the input messages.

        Returns:
            dict: A dictionary containing the outputs of the tool executions.
        """
        if messages := inputs.get("messages", []):
            message = messages[-1]
        else:
            raise ValueError("No message found in input")
        outputs = []
        for tool_call in message.tool_calls:
            print("🛠 tool_call:", tool_call)
            try:
                tool_result = await self.tools_by_name[tool_call["name"]].ainvoke(
                    tool_call["args"]
                )
                print("✅ tool_result:", tool_result)

                outputs.append(
                    ToolMessage(
                        content=json.dumps(tool_result),
                        name=tool_call["name"],
                        tool_call_id=tool_call.get("id", "unknown"),
                    )
                )
            except Exception as e:
                import traceback

                print("🔥 Error during tool execution:")
                traceback.print_exc()
                outputs.append(
                    ToolMessage(
                        content=f"Error: {e}",
                        name=tool_call["name"],
                        tool_call_id=tool_call.get("id", "unknown"),
                    )
                )
            except Exception as e:
                import traceback

                print("🔥 Unexpected error during tool execution:")
                traceback.print_exc()
                outputs.append(
                    ToolMessage(
                        content=f"Unexpected Error: {e}",
                        name=tool_call["name"],
                        tool_call_id=tool_call.get("id", "unknown"),
                    )
                )
        return {"messages": outputs}


async def build_graph(client):
    """
    Builds the agent graph.

    Args:
        client: The client used to interact with the agent.

    Returns:
        The compiled agent graph.
    """
    graph_builder = StateGraph(State)

    llm = get_llm()
    tools = client.get_tools()
    llm_with_tools = llm.bind_tools(tools)

    def chatbot(state: State):
        """
        The chatbot node in the graph.

        Args:
            state (State): The current state of the graph.

        Returns:
            dict: A dictionary containing the output message from the LLM.
        """
        return {"messages": [llm_with_tools.invoke(state["messages"])]}

    # The first argument is the unique node name
    # The second argument is the function or object that will be called whenever
    # the node is used.
    graph_builder.add_node("chatbot", chatbot)

    tool_node = BasicToolNode(tools)
    graph_builder.add_node("tools", tool_node)

    # The `tools_condition` function returns "tools" if the chatbot asks to use a tool, and "END" if
    # it is fine directly responding. This conditional routing defines the main agent loop.
    graph_builder.add_conditional_edges(
        "chatbot",
        route_tools,
        # The following dictionary lets you tell the graph to interpret the condition's outputs as a specific node
        # It defaults to the identity function, but if you
        # want to use a node named something else apart from "tools",
        # You can update the value of the dictionary to something else
        # e.g., "tools": "my_tools"
        {"tools": "tools", END: END},
    )
    # Any time a tool is called, we return to the chatbot to decide the next step
    graph_builder.add_edge("tools", "chatbot")

    graph_builder.add_edge(START, "chatbot")
    return graph_builder.compile()


def route_tools(
    state: State,
):
    """
    Routes the graph to the ToolNode if the last message has tool calls.
    Otherwise, route to the end.

    Args:
        state (State): The current state of the graph.

    Returns:
        str: "tools" if the last message has tool calls, otherwise END.
    """
    if isinstance(state, list):
        ai_message = state[-1]
    elif messages := state.get("messages", []):
        ai_message = messages[-1]
    else:
        raise ValueError(f"No messages found in input state to tool_edge: {state}")
    if hasattr(ai_message, "tool_calls") and len(ai_message.tool_calls) > 0:
        return "tools"
    return END
