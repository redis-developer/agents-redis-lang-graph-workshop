import os

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_ollama import OllamaEmbeddings
from langchain_redis import RedisConfig, RedisVectorStore

load_dotenv()

REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
INDEX_NAME = os.environ.get("VECTOR_INDEX_NAME", "oregon_trail")

config = RedisConfig(index_name=INDEX_NAME, redis_url=REDIS_URL)

doc = Document(
    page_content="the northern trail, of the blue mountains, was destroyed by a flood and is no longer safe to traverse. It is recommended to take the southern trail although it is longer."
)


def get_vector_store():
    if os.environ.get("MODEL_NAME") == "ollama":
        return __get_ollama_vector_store()
    elif os.environ.get("MODEL_NAME") == "openai":
        return __get_openai_vector_store()

def __check_existing_embedding(vector_store):
    results = vector_store.similarity_search(doc, k=1)
    if not results:
        raise Exception("Required content not found in existing store")

def __get_ollama_vector_store():
    try:
        config.from_existing = True
        vector_store = RedisVectorStore(OllamaEmbeddings(model="llama3"), config=config)
        __check_existing_embedding(vector_store)
    except:
        print("Init vector store with document")
        config.from_existing = False
        vector_store = RedisVectorStore.from_documents(
            [doc], OllamaEmbeddings(model="nomic-embed-text"), config=config
        )
    return vector_store

def __get_openai_vector_store():
    try:
        config.from_existing = True
        vector_store = RedisVectorStore(OpenAIEmbeddings(), config=config)
        __check_existing_embedding(vector_store)
    except:
        print("Init vector store with document")
        config.from_existing = False
        vector_store = RedisVectorStore.from_documents(
            [doc], OpenAIEmbeddings(), config=config
        )
    return vector_store
