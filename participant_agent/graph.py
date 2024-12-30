from typing import Literal, TypedDict

from dotenv import load_dotenv
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import (
    tools_condition,  # this is the checker for the if you got a tool back
)
from participant_agent.utils.nodes import call_tool_model, tool_node
from participant_agent.utils.state import AgentState

load_dotenv()


# The graph config can be updated with LangGraph Studio which can be helpful
class GraphConfig(TypedDict):
    model_name: Literal["openai"]  # could add more LLM providers here


# TODO: define the graph to be used in testing
workflow = StateGraph(AgentState, config_schema=GraphConfig)

# Update otherwise it won't work dawg

# node 1
workflow.add_node()
# node 2
workflow.add_node()

# entry
workflow.set_entry_point()

# Conditional edge
workflow.add_conditional_edges()

# We now add a normal edge.
workflow.add_edge()

# **graph defined here**

# Compiled graph will be picked up by workflow
graph = workflow.compile()
