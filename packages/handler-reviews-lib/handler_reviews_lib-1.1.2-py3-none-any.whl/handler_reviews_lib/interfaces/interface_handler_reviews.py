from abc import ABC, abstractmethod


class IHandlerReviews(ABC):
    @abstractmethod
    def get_response(self, **kwargs) -> str:
        pass
