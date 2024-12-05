from abc import ABC, abstractmethod


class GamePlayInterface(ABC):
    @abstractmethod
    def get_graph(self):
        """This function should return the compiled graph to be evaluated in the game."""
        pass

    @abstractmethod
    def get_semantic_cache(self):
        """if implementing a semantic cache, this function should return the cache object to preform checks against."""
        pass
