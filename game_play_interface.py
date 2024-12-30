from abc import ABC


class GamePlayInterface(ABC):
    @property
    def router(self):
        """Return the router instance."""
        pass

    @property
    def semantic_cache(self):
        """Return the semantic cache instance."""
        pass

    @property
    def graph(self):
        """Return the graph instance."""
        pass
