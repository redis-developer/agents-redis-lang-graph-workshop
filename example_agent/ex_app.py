from example_agent.utils.ex_router import router
from example_agent.utils.ex_semantic_cache import semantic_cache
from game_play_interface import GamePlayInterface

from .ex_graph import graph


class ExampleApp(GamePlayInterface):
    def __init__(self):
        self._router = router
        self._semantic_cache = semantic_cache
        self._graph = graph

    def graph(self):
        return self._graph

    def semantic_cache(self):
        return self._semantic_cache

    def router(self):
        return self._router
