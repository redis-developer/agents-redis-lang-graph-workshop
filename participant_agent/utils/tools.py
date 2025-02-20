import os

from dotenv import load_dotenv
from langchain.tools.retriever import create_retriever_tool
from langchain_core.documents import Document
from langchain_core.tools import tool
from langchain_openai import OpenAIEmbeddings
from langchain_redis import RedisVectorStore
from pydantic import BaseModel, Field

from .vector_store import get_vector_store

load_dotenv()

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")


@tool
def multiply(a: int, b: int) -> int:
    """multiply two numbers."""
    return a * b


# TODO: define restock pydantic model for structure input
class RestockInput(BaseModel):
    pass


# TODO: modify to accept correct inputs and have meaningful docstring
@tool("restock-tool", args_schema=RestockInput)
def restock_tool() -> int:
    """some description"""
    pass


# TODO: implement the retriever tool
## update get_vector_store function
# vector_store = get_vector_store()
## update tool with appropriate information so the agent knows how to invoke
# retriever_tool = create_retriever_tool()

# TODO: pass the retriever_tool and restock tool multiply is only meant as an example
# tools = [retriever_tool, restock_tool]
tools = [multiply]
