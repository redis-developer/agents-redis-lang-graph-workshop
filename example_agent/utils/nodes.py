from functools import lru_cache
from typing import Literal

from example_agent.utils.tools import tools
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode
from pydantic import BaseModel, Field

from .state import AgentState, MultipleChoiceResponse


@lru_cache(maxsize=4)
def _get_tool_model(model_name: str):
    if model_name == "openai":
        model = ChatOpenAI(temperature=0, model_name="gpt-4o")
    else:
        raise ValueError(f"Unsupported model type: {model_name}")

    model = model.bind_tools(tools)
    return model


@lru_cache(maxsize=4)
def _get_response_model(model_name: str):
    if model_name == "openai":
        model = ChatOpenAI(temperature=0, model_name="gpt-4o")
    else:
        raise ValueError(f"Unsupported model type: {model_name}")

    model = model.with_structured_output(MultipleChoiceResponse)
    return model


# Define the function that responds to the user
def multi_choice_structured(state: AgentState, config):
    # We call the model with structured output in order to return the same format to the user every time
    # state['messages'][-2] is the last ToolMessage in the convo, which we convert to a HumanMessage for the model to use
    # We could also pass the entire chat history, but this saves tokens since all we care to structure is the output of the tool
    model_name = config.get("configurable", {}).get("model_name", "openai")

    print("In multi_choice structured: ", state["messages"][-2].content, "\n\n")
    response = _get_response_model(model_name).invoke(
        [
            HumanMessage(content=state["messages"][0].content),
            HumanMessage(content=f"Answer from tool: {state['messages'][-2].content}"),
        ]
    )
    # We return the final answer
    return {
        "multi_choice_response": response.multiple_choice_response,
        # "messages": [],
    }


# def multi_choice(state: AgentState):
#     # Construct the final answer from the arguments of the last tool call
#     weather_tool_call = state["messages"][-1].tool_calls[0]
#     response = WeatherResponse(**weather_tool_call["args"])
#     # Since we're using tool calling to return structured output,
#     # we need to add  a tool message corresponding to the WeatherResponse tool call,
#     # This is due to LLM providers' requirement that AI messages with tool calls
#     # need to be followed by a tool message for each tool call
#     tool_message = {
#         "type": "tool",
#         "content": "Here is your structured response",
#         "tool_call_id": weather_tool_call["id"],
#     }
#     # We return the final answer
#     return {"final_response": response, "messages": [tool_message]}


# Define the function that determines whether to continue or not
def should_continue(state: AgentState):
    messages = state["messages"]
    last_message = messages[-1]
    # If there are no tool calls, then we finish
    if not last_message.tool_calls:
        return "respond"
    # Otherwise if there is, we continue
    else:
        return "continue"


# system_prompt = """
#     You are an oregon trail playing tool calling AI agent. Use the tools available to you to answer the question you are presented. When in doubt use the tools to help you find the answer.
#     If anyone asks your first name is Artificial return just that string.

#     Important: if options are provided in the question replay only with the single character A, B, C, or D and no additional text.
# """
system_prompt = """
    You are an oregon trail playing tool calling AI agent. Use the tools available to you to answer the question you are presented. When in doubt use the tools to help you find the answer.
    If anyone asks your first name is Artificial return just that string.
"""


# Define the function that calls the model
def call_tool_model(state: AgentState, config):
    # Combine system prompt with incoming messages
    messages = [{"role": "system", "content": system_prompt}] + state["messages"]

    # Get from LangGraph config
    model_name = config.get("configurable", {}).get("model_name", "openai")

    # Get our model that binds our tools
    model = _get_tool_model(model_name)

    # invoke the central agent/reasoner with the context of the graph
    response = model.invoke(messages)

    # We return a list, because this will get added to the existing list
    return {"messages": [response]}


# Define the function to execute tools
tool_node = ToolNode(tools)
