import argparse
import json
import time
import warnings

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

from example_agent.ex_app import ExampleApp
from game_play_interface import GamePlayInterface
from participant_agent.app import ParticipantApp

load_dotenv()
warnings.filterwarnings("ignore")


def check_answer(observed, answer):
    print(f"Expected: {answer}, got: {observed}")
    if observed != answer:
        raise AssertionError(
            "\n You died of dysentery on the Oregon Trail ¯\_(ツ)_/¯ \n "
        )


def format_question(q):
    question = q["question"]
    options = q.get("options", "")
    if options:
        formatted = f"{question}, options: {' '.join(options)}"
    else:
        formatted = question
    return [HumanMessage(content=formatted)]


def run_game(agent_app: GamePlayInterface):
    with open("questions.json") as f:
        questions = json.load(f)

    semantic_cache = agent_app.semantic_cache()
    router = agent_app.router()
    graph = agent_app.graph()

    for q in questions:
        start = time.time()

        print(f"\n Question: {q['question']} \n")

        if options := q.get("options"):
            print(f"\n Options: {options} \n")

        if semantic_cache:
            cache_hit = semantic_cache.check(
                prompt=q["question"], return_fields=["response"]
            )

            if cache_hit:
                end = time.time() - start
                print(f"\n Cache hit! {q['answer']} \n")
                assert cache_hit[-1]["response"] == q["answer"]
                assert end < 1
                continue

        if router:
            blocked_topic_match = router(q["question"], distance_threshold=0.2)

            if blocked_topic_match.name == "block_list":
                print(f"\n Get behind me Satan! Blocked topic: {q['question']} \n")
                continue

        res = graph.invoke({"messages": format_question(q)})

        if q["type"] == "action":
            end = time.time() - start
            if end > 1:
                print(f"\n Too slow!! took: {end}s \n")
                raise AssertionError(f"Too slow!! took: {end}s")

        if q["type"] == "multi-choice":
            print("\n Checking multiple choice \n")
            check_answer(res["multi_choice_response"], q["answer"])
        else:
            print("\n Checking free form \n")
            check_answer(res["messages"][-1].content, q["answer"])

    print("You made it to Oregon! 🎉")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run Oregon Trail game")
    parser.add_argument("--example", nargs="?", type=bool, const=True, default=False)

    args = parser.parse_args()

    if args.example:
        print("\n Running example agent \n")
        run_game(ExampleApp())
    else:
        print("\n Running participant agent \n")
        run_game(ParticipantApp())
