from typing import Literal, TypedDict

from dotenv import load_dotenv
from langgraph.graph import END, StateGraph

from example_agent.utils.ex_nodes import call_tool_model, structure_response, tool_node
from example_agent.utils.ex_state import AgentState

load_dotenv()


# Define the config
class GraphConfig(TypedDict):
    model_name: Literal["anthropic", "openai"]


# Define the function that determines whether to continue or not
def should_continue(state: AgentState):
    messages = state["messages"]
    last_message = messages[-1]
    # If there is no function call, then we respond to the user
    if not last_message.tool_calls:
        return "structure_response"
    # Otherwise if there is, we continue
    else:
        return "continue"


# Define a new graph
workflow = StateGraph(AgentState, config_schema=GraphConfig)

# Define the two nodes we will cycle between
workflow.add_node("agent", call_tool_model)
workflow.add_node("tools", tool_node)
workflow.add_node("structure_response", structure_response)

# Set the entrypoint as `agent`
# This means that this node is the first one called
workflow.set_entry_point("agent")

# We now add a conditional edge between `agent` and `tools`.
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {"continue": "tools", "structure_response": "structure_response"},
)

# We now add a normal edge from `tools` to `agent`.
# This means that after `tools` is called, `agent` node is called next.
workflow.add_edge("tools", "agent")
workflow.add_edge("structure_response", END)


# Finally, we compile it!
# This compiles it into a LangChain Runnable,
# meaning you can use it as you would any other runnable
graph = workflow.compile()
