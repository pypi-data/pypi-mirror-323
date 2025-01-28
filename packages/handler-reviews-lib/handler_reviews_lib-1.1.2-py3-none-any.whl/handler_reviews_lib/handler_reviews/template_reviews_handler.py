import random
from abc import ABC
from handler_reviews_lib.interfaces.interface_handler_reviews import IHandlerReviews


class TemplateReviewsHandler(IHandlerReviews, ABC):
    def __init__(self, templates: dict):
        self.templates = templates
    signs: list = ["!", "."]

    def get_response(self, name_client: str, grade: int) -> str:
        greeting_key = 'greeting'
        final_key = 'final'
        answer = self._update_answer(reviews=self.templates, answer='', name=name_client, key=greeting_key)
        answer = self._update_answer(reviews=self.templates['gratitude'], grade=grade, answer=answer)
        answer = self._update_answer(reviews=self.templates['main_text'], grade=grade, answer=answer)
        answer = self._update_answer(reviews=self.templates, answer=answer,key=final_key)
        return answer

    def _update_answer(self, reviews: dict, grade=None, answer='', name=None, key='') -> str:
        review = ''
        if grade is None:
            review = random.choice(reviews[key])
        if grade == 5 or grade == 4:
            review = random.choice(reviews["54"])
        elif grade == 3:
            review = random.choice(reviews['3'])
        elif grade is not None and grade < 3:
            review = random.choice(reviews['21'])

        if name is not None:
            response = f"{review}, {name}"
        else:
            response = f'{answer} {review}'
        return self._add_sign(response)

    def _add_sign(self, answer: str) -> str:
        return f"{answer}{random.choice(self.signs)}"

