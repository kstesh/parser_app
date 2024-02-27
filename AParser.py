from abc import ABC, abstractmethod


class AParser(ABC):
    @abstractmethod
    def __init__(self, term: str):
        pass

    @abstractmethod
    def search(self):
        pass




