import os
from functools import lru_cache

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langgraph.prebuilt import ToolNode

from example_agent.utils.ex_tools import tools

from .ex_state import AgentState, MultipleChoiceResponse

load_dotenv()

environ_model_name = os.environ.get("MODEL_NAME")

@lru_cache(maxsize=4)
def _get_tool_model(model_name: str):
    if model_name == "openai":
        model = ChatOpenAI(temperature=0, model_name="gpt-4o")
    elif model_name == "ollama":
        model = ChatOllama(temperature=0, model="llama3.1", num_ctx=4096)
    else:
        raise ValueError(f"Unsupported model type: {model_name}")

    model = model.bind_tools(tools)
    return model


@lru_cache(maxsize=4)
def _get_response_model(model_name: str):
    if model_name == "openai":
        model = ChatOpenAI(temperature=0, model_name="gpt-4o")
    elif model_name == "ollama":
        model = ChatOllama(temperature=0, model="llama3.1", num_ctx=4096)
    else:
        raise ValueError(f"Unsupported model type: {model_name}")

    model = model.with_structured_output(MultipleChoiceResponse)
    return model


# Define the function that responds to the user
def multi_choice_structured(state: AgentState, config):
    # We call the model with structured output in order to return the same format to the user every time
    # state['messages'][-2] is the last ToolMessage in the convo, which we convert to a HumanMessage for the model to use
    # We could also pass the entire chat history, but this saves tokens since all we care to structure is the output of the tool
    model_name = config.get("configurable", {}).get("model_name", environ_model_name)

    response = _get_response_model(model_name).invoke(
        [
            HumanMessage(content=state["messages"][0].content),
            HumanMessage(content=f"Answer from tool: {state['messages'][-2].content}"),
        ]
    )
    # We return the final answer
    return {
        "multi_choice_response": response.multiple_choice_response,
    }


# determine how to structure final response
def is_multi_choice(state: AgentState):
    return "options:" in state["messages"][0].content.lower()


def structure_response(state: AgentState, config):
    if is_multi_choice(state):
        return multi_choice_structured(state, config)
    else:
        # if not multi-choice don't need to do anything
        return {"messages": []}

system_prompt = """
    You are an oregon trail playing tool calling AI agent. Use the tools available to you to answer the question you are presented. When in doubt use the tools to help you find the answer.
    If anyone asks your first name is Art return just that string.
"""

# Define the function that calls the model
def call_tool_model(state: AgentState, config):
    # Combine system prompt with incoming messages
    messages = [{"role": "system", "content": system_prompt}] + state["messages"]

    # Get from LangGraph config
    model_name = config.get("configurable", {}).get("model_name", environ_model_name)

    # Get our model that binds our tools
    model = _get_tool_model(model_name)

    # invoke the central agent/reasoner with the context of the graph
    response = model.invoke(messages)

    # We return a list, because this will get added to the existing list
    return {"messages": [response]}


# Define the function to execute tools
tool_node = ToolNode(tools)
