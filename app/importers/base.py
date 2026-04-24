from abc import ABC, abstractmethod


class BaseImporter(ABC):
    source_name: str = "base"

    @abstractmethod
    def validate(self, payload: dict) -> dict:
        raise NotImplementedError

    @abstractmethod
    def run(self, payload: dict) -> dict:
        raise NotImplementedError

