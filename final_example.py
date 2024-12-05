from game_play import GamePlayInterface
from langchain.tools.retriever import create_retriever_tool
from langchain_core.documents import Document
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_redis import RedisVectorStore
from langgraph.graph import START, MessagesState, StateGraph
from langgraph.prebuilt import (
    tools_condition,  # this is the checker for the if you got a tool back
)
from langgraph.prebuilt import ToolNode
from redisvl.extensions.llmcache import SemanticCache

# Semantic cache
hunting_example = "There's a deer. You're hungry. You know what you have to do..."

semantic_cache = SemanticCache(
    name="oregon_trail_cache",
    redis_url="redis://localhost:6379/0",
    distance_threshold=0.1,
)

semantic_cache.store(prompt=hunting_example, response="bang")


# System message
SYS_MSG = SystemMessage(
    content="You are an oregon trail playing AI agent. Use the tools available to answer the questions provided. Important: if options are provided in the question replay only with the single character A, B, C, or D and no additional text."
)


## define tools
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
    "retrieve_trail_tips",
    "Search and return information that is helpful for answering questions about what to do next on the Oregon Trail",
)

tools = [retriever_tool]

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
