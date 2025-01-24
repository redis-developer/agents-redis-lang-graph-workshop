from typing import Literal, TypedDict

from dotenv import load_dotenv
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import (
    tools_condition,  # this is the checker for the if you got a tool back
)

from participant_agent.utils.nodes import call_tool_model, structure_response, tool_node
from participant_agent.utils.state import AgentState

load_dotenv()


# The graph config can be updated with LangGraph Studio which can be helpful
class GraphConfig(TypedDict):
    model_name: Literal["openai"]  # could add more LLM providers here


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


# TODO: define the graph to be used in testing
# workflow = StateGraph(AgentState, config_schema=GraphConfig)

# # Update otherwise it won't work dawg

# # node 1
# workflow.add_node()
# # node 2
# workflow.add_node()

# # entry
# workflow.set_entry_point()

# # Conditional edge
# workflow.add_conditional_edges()

# # We now add a normal edge.
# workflow.add_edge()

# # **graph defined here**

# # Compiled graph will be picked up by workflow
# graph = workflow.compile()
graph = None
