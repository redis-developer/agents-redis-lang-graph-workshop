from functools import lru_cache

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode
from participant_agent.utils.tools import tools

from .state import AgentState


# need to use this in call_tool_model function
@lru_cache(maxsize=4)
def _get_tool_model(model_name: str):
    """
    This function initializes the model to be used to determine tools can be modified to support additional LLM providers.
    """
    if model_name == "openai":
        model = ChatOpenAI(temperature=0, model_name="gpt-4o")
    else:
        raise ValueError(f"Unsupported model type: {model_name}")

    model = model.bind_tools(tools)
    return model


# TODO: define meaningful system prompt for Agent
system_prompt = """You are an Agent that plays the Oregon Trail"""


# TODO: define the interaction between agent, tools, and messages
# This is a critical part of creating agents and understanding the flow of messages
def call_tool_model(state: AgentState, config):
    # Combine system prompt with incoming messages
    messages = [{"role": "system", "content": _}] + state["messages"]

    # Get from LangGraph config
    model_name = config.get("configurable", {}).get("model_name", "openai")

    # Get our model that binds our tools
    model = _get_tool_model(_)

    # invoke the central agent/reasoner with the context of the graph
    response = model.invoke(_)

    # We return a list, because this will get added to the existing list
    return {"messages": [response]}


# Define the function to execute tools
tool_node = ToolNode(tools)
