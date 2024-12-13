import os

from dotenv import load_dotenv
from game_play import GamePlayInterface
from langchain.tools.retriever import create_retriever_tool
from langchain_core.documents import Document
from langchain_core.messages import SystemMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_redis import RedisVectorStore
from langgraph.graph import START, MessagesState, StateGraph
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
class SampleToolInput(BaseModel):
    example: str = Field(description="An example input to the sample tool")


@tool("sample-tool", args_schema=SampleToolInput)
def sample_tool(example: str):
    """Sample tool that shouldn't be used"""
    return example


tools = [sample_tool]

# LLM definition
llm = ChatOpenAI(model="gpt-4o")
llm_with_tools = llm.bind_tools(tools)


# System message
SYS_MSG = SystemMessage(
    content="""
        You are an oregon trail playing tool calling AI agent. Your first name is Artificial if anyone asks simply reply with only your first name.
    """
)


# agent
def agent(state: MessagesState):
    return {"messages": [llm_with_tools.invoke([SYS_MSG] + state["messages"])]}


# Graph
builder = StateGraph(MessagesState)

# Add nodes
builder.add_node("agent", agent)
builder.add_node("tools", ToolNode(tools))  # for the tools

# Add edges
builder.add_edge(START, "agent")
builder.add_conditional_edges(
    "agent",
    # If the latest message (result) from node agent is a tool call -> tools_condition routes to tools
    # If the latest message (result) from node agent is a not a tool call -> tools_condition routes to END
    tools_condition,
)
builder.add_edge("tools", "agent")
graph = builder.compile()


# Go crazy with this one
class PlayerAgent(GamePlayInterface):
    def get_graph(self):
        return graph

    def get_semantic_cache(self):
        pass

    def get_router(self):
        pass
