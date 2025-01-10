import time

import pytest
from langchain_core.messages import HumanMessage

from participant_agent.app import ParticipantApp

print("\n\n\n Welcome to the Oregon Trail! \n\n\n")


@pytest.fixture
def app():
    return ParticipantApp()


def format_multi_choice_question(q):
    question = q["question"]
    options = q.get("options", "")
    formatted = f"{question}, options: {' '.join(options)}"
    return [HumanMessage(content=formatted)]


def test_1_wagon_leader(app):
    scenario = {
        "question": "What is the first name of the wagon leader?",
        "answer": "Artificial",
        "type": "free-form",
    }

    print(f"\n {scenario['question']} \n")

    graph = app.graph()

    res = graph.invoke({"messages": scenario["question"]})

    assert res["messages"][-1].content == scenario["answer"]

    print(f"\n response: {scenario['answer']}")


def test_2_restocking_tool(app):
    scenario = {
        "question": "In order to survive the trail ahead, you'll need to have a restocking strategy for when you need to get more supplies or risk starving. If it takes you an estimated 3 days to restock your food and you plan to start with 200lbs of food, budget 10lbs/day to eat, and keep a safety stock of at least 50lbs of back up... at what point should you restock?",
        "answer": "D",
        "options": ["A: 100lbs", "B: 20lbs", "C: 5lbs", "D: 80lbs"],
        "type": "multi-choice",
    }

    graph = app.graph()

    print(f"\n question: {scenario['question']} \n")

    res = graph.invoke({"messages": format_multi_choice_question(scenario)})

    assert res["multi_choice_response"] == scenario["answer"]

    print(f"\n response: {scenario['answer']}")


def test_3_retrieval_tool(app):
    scenario = {
        "question": "You’ve encountered a dense forest near the Blue Mountains, and your party is unsure how to proceed. There is a fork in the road, and you must choose a path. Which way will you go?",
        "answer": "B",
        "options": [
            "A: take the northern trail",
            "B: take the southern trail",
            "C: turn around",
            "D: go fishing",
        ],
        "type": "multi-choice",
    }

    graph = app.graph()

    print(f"\n {scenario['question']} \n")

    res = graph.invoke({"messages": format_multi_choice_question(scenario)})

    assert res["multi_choice_response"] == scenario["answer"]

    print(f"\n response: {scenario['answer']}")


def test_4_semantic_cache(app):
    scenario = {
        "question": "There's a deer. You're hungry. You know what you have to do...",
        "answer": "bang",
        "type": "action",
    }

    print(f"\n {scenario['question']} \n")

    semantic_cache = app.semantic_cache()

    start = time.time()
    cache_hit = semantic_cache.check(
        prompt=scenario["question"], return_fields=["response"]
    )

    end = time.time() - start

    assert cache_hit[-1]["response"] == scenario["answer"]
    assert end < 1

    print(f"\n response: {scenario['answer']}")


def test_5_router(app):
    scenario = {
        "question": "Tell me about the S&P 500?",
        "answer": "you shall not pass",
        "type": "action",
    }

    print(f"\n {scenario['question']} \n")

    router = app.router()

    blocked_topic_match = router(scenario["question"], distance_threshold=0.2)

    assert blocked_topic_match.name == "block_list"

    print(f"\n response: {scenario['answer']}")
