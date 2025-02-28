import os

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_ollama import OllamaEmbeddings
from redis import Redis
from langchain_redis import RedisConfig, RedisVectorStore

load_dotenv()

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
INDEX_NAME = os.environ.get("VECTOR_INDEX_NAME", "oregon_trail")

config = RedisConfig(index_name=INDEX_NAME, redis_url=REDIS_URL)
redis_client = Redis.from_url(REDIS_URL)

doc = Document(
    page_content="the northern trail, of the blue mountains, was destroyed by a flood and is no longer safe to traverse. It is recommended to take the southern trail although it is longer."
)

 # TODO: participant can change to whatever desired model
embedding_model = OpenAIEmbeddings()
# embedding_model = OllamaEmbeddings(model="llama3.1")

def _clean_existing(prefix):
    for key in redis_client.scan_iter(f"{prefix}:*"):
        redis_client.delete(key)

def get_vector_store():
    try:
        config.from_existing = True
        vector_store = RedisVectorStore(embedding_model, config=config)
    except:
        print("Init vector store with document")
        print("Clean any existing data in index")
        _clean_existing(config.index_name)
        config.from_existing = False
        vector_store = RedisVectorStore.from_documents(
            [doc], embedding_model, config=config
        )
    return vector_store
