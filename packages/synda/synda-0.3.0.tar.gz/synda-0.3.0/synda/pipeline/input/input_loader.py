from abc import abstractmethod


class InputLoader:
    @abstractmethod
    def load(self) -> None:
        pass
