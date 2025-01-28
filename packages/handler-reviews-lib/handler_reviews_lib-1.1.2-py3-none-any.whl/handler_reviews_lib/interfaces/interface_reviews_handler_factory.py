import enum
from abc import ABC, abstractmethod
from handler_reviews_lib.interfaces.interface_handler_reviews import IHandlerReviews


class IHandlerFactory(ABC):
    @abstractmethod
    def fetch_handler(self, handler_type: enum, **kwargs) -> IHandlerReviews:
        pass

