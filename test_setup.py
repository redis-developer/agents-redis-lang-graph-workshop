import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from redis import Redis

load_dotenv()

if os.environ.get("MODEL_NAME") == "openai":
    llm = ChatOpenAI(model="gpt-4o")
elif os.environ.get("MODEL_NAME") == "ollama":
    llm = ChatOllama(model="llama3.1")
else:
    raise Exception("Setup failed, MODEL_NAME not defined in .env")

client = Redis.from_url(os.environ.get("REDIS_URL"))


def test_setup():
    assert llm.invoke(["Hello, how are you?"])
    assert client.ping()

    print("Setup worked")


if __name__ == "__main__":
    test_setup()
