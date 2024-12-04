import json
import time

from final_example import graph, semantic_cache
from langchain_core.messages import HumanMessage


def format_question(q):
    question = q["question"]
    options = q.get("options", "")
    if options:
        formatted = f"{question}, options: {' '.join(options)}"
    else:
        formatted = question
    return [HumanMessage(content=formatted)]


def run_game():
    with open("questions.json") as f:
        questions = json.load(f)

    for q in questions:
        start = time.time()
        cache_hit = semantic_cache.check(
            prompt=q["question"], return_fields=["response"]
        )

        if cache_hit:
            end = time.time() - start
            assert cache_hit[-1]["response"] == q["answer"]
            assert end < 1
            continue

        res = graph.invoke({"messages": format_question(q)})

        try:
            assert res["messages"][-1].content == q["answer"]
        except AssertionError:
            print(f"Expected: {q['answer']}, got: {res['messages'][-1].content}")
            raise AssertionError("\n You have failed the Oregon Trail ¯\_(ツ)_/¯ \n ")

    print("You made it to Oregon! 🎉")


if __name__ == "__main__":
    run_game()
