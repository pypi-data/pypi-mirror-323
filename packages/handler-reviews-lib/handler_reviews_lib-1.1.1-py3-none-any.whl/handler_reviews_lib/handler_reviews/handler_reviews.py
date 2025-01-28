import enum
from abc import ABC
from handler_reviews_lib.handler_reviews.enums_type import HandlerType
from handler_reviews_lib.handler_reviews.gpt_reviews_handler import GPTReviewsHandler
from handler_reviews_lib.handler_reviews.template_reviews_handler import TemplateReviewsHandler
from handler_reviews_lib.interfaces.interface_handler_reviews import IHandlerReviews
from handler_reviews_lib.interfaces.interface_reviews_handler_factory import IHandlerFactory


class HandlerReviews(IHandlerFactory, ABC):
    def fetch_handler(self, handler_type: enum, **kwargs) -> IHandlerReviews:
        if handler_type == HandlerType.TEMPLATEHANDLER:
            return TemplateReviewsHandler(**kwargs)
        elif handler_type == HandlerType.GPTHANDLER:
            return GPTReviewsHandler(**kwargs)
        else:
            raise ValueError("Handler type not found")



