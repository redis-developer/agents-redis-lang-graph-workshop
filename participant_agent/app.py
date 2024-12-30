from game_play_interface import GamePlayInterface
from participant_agent.utils.router import router
from participant_agent.utils.semantic_cache import semantic_cache

from .graph import graph


class ParticipantApp(GamePlayInterface):
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
