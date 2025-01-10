import os

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from redis import Redis

load_dotenv()

llm = ChatOpenAI(model="gpt-4o")
client = Redis.from_url(os.environ.get("REDIS_URL"))


def test_setup():
    assert llm.invoke(["Hello, how are you?"])
    assert client.ping()

    print("Setup worked")


if __name__ == "__main__":
    test_setup()
