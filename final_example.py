import os

from dotenv import load_dotenv
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

from workshop.game_play_interface import GamePlayInterface

load_dotenv()

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

# Semantic router
blocked_references = [
    "thinks about aliens",
    "corporate questions about agile",
    "anything about the S&P 500",
]

block_route = Route(name="block_list", references=blocked_references)

router = SemanticRouter(
    name="bouncer",
    vectorizer=HFTextVectorizer(),
    routes=[block_route],
    redis_url=REDIS_URL,
    overwrite=True,
)


# Semantic cache
hunting_example = "There's a deer. You're hungry. You know what you have to do..."

semantic_cache = SemanticCache(
    name="oregon_trail_cache",
    redis_url=REDIS_URL,
    distance_threshold=0.1,
)

semantic_cache.store(prompt=hunting_example, response="bang")


# System message
SYS_MSG = SystemMessage(
    content="""
        You are an oregon trail playing tool calling AI agent. Use the tools available to you to answer the question you are presented. When in doubt use the tools to help you find the answer.

        Important: if options are provided in the question replay only with the single character A, B, C, or D and no additional text.
    """
)


## define tools

## custom tool


class RestockInput(BaseModel):
    daily_usage: int = Field(
        description="Pounds (lbs) of food expected to be consumed daily"
    )
    lead_time: int = Field(description="Lead time to replace food in days")
    safety_stock: int = Field(
        description="Number of pounds (lbs) of safety stock to keep on hand"
    )


@tool("restock-tool", args_schema=RestockInput)
def restock_tool(daily_usage: int, lead_time: int, safety_stock: int) -> int:
    """restock formula tool used specifically for calculating the amount of food at which you should start restocking."""
    print(f"Using restock tool!: {daily_usage=}, {lead_time=}, {safety_stock=}")
    return (daily_usage * lead_time) + safety_stock


## retriever tool
doc = Document(
    page_content="the northern trail, of the blue mountains, was destroyed by a flood and is no longer safe to traverse. It is recommended to take the southern trail although it is longer."
)

# TODO: I like the idea of them having to populate the index themselves but it may be worth thinking about if we set this up ahead of time.
vectorstore = RedisVectorStore.from_documents(
    [doc],
    OpenAIEmbeddings(),
    redis_url="redis://localhost:6379/0",
    index_name="oregon_trail",
)

retriever_tool = create_retriever_tool(
    vectorstore.as_retriever(),
    "get_directions",
    "Search and return information related to which routes/paths/trails to take along your journey.",
)

tools = [retriever_tool, restock_tool]

## define llm and bind with tools

# gpt-3.5-turbo gets stuck in loop
llm = ChatOpenAI(model="gpt-4o")
llm_with_tools = llm.bind_tools(tools)


## define nodes
def agent(state: MessagesState):
    if state["messages"][-1].name == "retrieve_trail_tips":
        return {
            "messages": [
                llm_with_tools.invoke(
                    [SYS_MSG]
                    + [
                        f"{state['messages'][0].content} consider context: {state['messages'][-1].content}"
                    ]
                )
            ]
        }
    else:
        return {"messages": [llm_with_tools.invoke([SYS_MSG] + state["messages"])]}


class ExampleAgent(GamePlayInterface):
    def get_graph(self):
        ## define graph

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
        return graph

    def get_semantic_cache(self):
        return semantic_cache

    def get_router(self):
        return router
