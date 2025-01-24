from functools import lru_cache

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import ToolNode

from participant_agent.utils.tools import tools

from .state import AgentState, MultipleChoiceResponse


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


#### For structured output


# TODO: this function will be used when using structured output
@lru_cache(maxsize=4)
def _get_response_model(model_name: str):
    if model_name == "openai":
        model = ChatOpenAI(temperature=0, model_name="gpt-4o")
    else:
        raise ValueError(f"Unsupported model type: {model_name}")

    # TODO: pass model for structured output
    model = model.with_structured_output()
    return model


# Define the function that responds to the user
def multi_choice_structured(state: AgentState, config):
    # We call the model with structured output in order to return the same format to the user every time
    # state['messages'][-2] is the last ToolMessage in the convo, which we convert to a HumanMessage for the model to use
    # We could also pass the entire chat history, but this saves tokens since all we care to structure is the output of the tool
    model_name = config.get("configurable", {}).get("model_name", "openai")

    response = _get_response_model(model_name).invoke(
        [
            HumanMessage(content=state["messages"][0].content),
            HumanMessage(content=f"Answer from tool: {state['messages'][-2].content}"),
        ]
    )

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


###


# TODO: define meaningful system prompt for Agent
system_prompt = ""


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
