import os

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_redis import RedisConfig, RedisVectorStore

load_dotenv()

REDIS_URL = os.environ.get("REDIS_URL", "redis://host.docker.internal:6379/0")
INDEX_NAME = os.environ.get("VECTOR_INDEX_NAME", "oregon_trail")

config = RedisConfig(index_name=INDEX_NAME, redis_url=REDIS_URL)

doc = Document(
    page_content="the northern trail, of the blue mountains, was destroyed by a flood and is no longer safe to traverse. It is recommended to take the southern trail although it is longer."
)


def get_vector_store():
    try:
        config.from_existing = True
        vector_store = RedisVectorStore(OpenAIEmbeddings(), config=config)
    except:
        print("Init vector store with document")
        config.from_existing = False

        # TODO: define vector store
        vector_store = None
    return vector_store
