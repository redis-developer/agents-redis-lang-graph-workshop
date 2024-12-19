import os

from dotenv import load_dotenv
from game_play import GamePlayInterface
from langchain.tools.retriever import create_retriever_tool
from langchain_core.documents import Document
from langchain_core.messages import SystemMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_redis import RedisVectorStore
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import (
    tools_condition,  # this is the checker for the if you got a tool back
)
from langgraph.prebuilt import ToolNode
from pydantic import BaseModel, Field
from redisvl.extensions.llmcache import SemanticCache
from redisvl.extensions.router import Route, SemanticRouter
from redisvl.utils.vectorize import HFTextVectorizer

# load necessary environment variables
load_dotenv()


# tool definitions
class RestockToolInput(BaseModel):
    daily_usage: int = Field(
        description="Pounds (lbs) of food expected to be consumed daily"
    )
    lead_time: int = Field(description="Lead time to replace food in days")
    safety_stock: int = Field(
        description="Number of pounds (lbs) of safety stock to keep on hand"
    )


class StructuredResponse(BaseModel):
    multi_choice_ans: str = Field(
        description="The response to the multiple choice question must only be a single character A, B, C, or D"
    )
    free_form_ans: str = Field(
        description="Response to the question beyond multiple choice"
    )


@tool("restock-tool", args_schema=RestockToolInput)
def restock_tool(daily_usage: int, lead_time: int, safety_stock: int) -> int:
    """restock formula tool used specifically for calculating the amount of food at which you should start restocking."""
    print(f"Using restock tool!: {daily_usage=}, {lead_time=}, {safety_stock=}")
    return (daily_usage * lead_time) + safety_stock


tools = [restock_tool, StructuredResponse]

# LLM definition
llm = ChatOpenAI(model="gpt-4o")
llm_with_tools = llm.bind_tools(tools)


# System message
SYS_MSG = SystemMessage(
    content="""
        You are an oregon trail playing tool calling AI agent. Your first name is Artificial if anyone asks simply reply with only your first name no preamble.
    """
)


# agent
def agent(state: MessagesState):
    return {"messages": [llm_with_tools.invoke([SYS_MSG] + state["messages"])]}


def respond(state: MessagesState):
    response = StructuredResponse(**state["messages"][-1].tool_calls[0]["args"])
    return {"final_response": response}


def should_continue(state: MessagesState):
    messages = state["messages"]
    last_message = messages[-1]
    if (
        len(last_message.tool_calls) == 1
        and last_message.tool_calls[0]["name"] == "StructuredResponse"
    ):
        return "respond"
    else:
        return "continue"


# Graph
builder = StateGraph(MessagesState)

# Add nodes
builder.add_node("agent", agent)
builder.add_node("respond", respond)
builder.add_node("tools", ToolNode(tools))  # for the tools

# Add edges
builder.add_edge(START, "agent")
builder.add_conditional_edges(
    "agent",
    should_continue,
    {
        "continue": "tools",
        "respond": "respond",
    },
)

builder.add_edge("tools", "agent")
builder.add_edge("respond", END)
graph = builder.compile()


# Go crazy with this one
class PlayerAgent(GamePlayInterface):
    def get_graph(self):
        return graph

    def get_semantic_cache(self):
        pass

    def get_router(self):
        pass
