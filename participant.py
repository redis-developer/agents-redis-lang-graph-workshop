from abc import ABC, abstractmethod


# Do not edit (or you won't pass)
class ParticipantInterface(ABC):
    @abstractmethod
    def compile_graph(self):
        pass


# Go crazy with this one
class PlayerAgent(ParticipantInterface):
    def compile_graph(self):
        pass
