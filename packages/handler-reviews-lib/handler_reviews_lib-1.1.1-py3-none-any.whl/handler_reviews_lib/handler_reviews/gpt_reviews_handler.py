from abc import ABC
from typing import Optional

import httpx
import tiktoken
from openai import OpenAI
from handler_reviews_lib.handler_reviews.enums_type import TypeModelChatGpt
from handler_reviews_lib.interfaces.interface_handler_reviews import IHandlerReviews


class GPTReviewsHandler(IHandlerReviews, ABC):
    tokens: Optional[int] = None
    _prompt: str = ("Ты Контент-Менеджер. Отвечай на отзывы клиентов о нашем товаре обращаясь по имени ,"
                   "если оно указано в соотвтествующем поле 'NAME' сообразно оценке пользователя."
                   " Пример ответа: Добрый день, Олег! Спасибо что поставили 5 нашему товару! "
                   "Мы ждем вас снова!")

    def __init__(self, api_key: str, model: TypeModelChatGpt, proxy_url: str, prompt=""):
        self.tokens = None
        self.openai_client = OpenAI(api_key=api_key,
                                    default_headers={"OpenAI-Beta": "assistants=v1"},
                                    http_client=httpx.Client(proxy=proxy_url))
        self.model = model.value
        self.prompt = prompt
        self._encoding = tiktoken.encoding_for_model(model.value)
        self.chat_completion = self.openai_client.chat.completions

    def get_response(self, name_client: str, review: str, grade: int, return_amount_tokens=False) -> str:
        model = str(self.model)
        if self.prompt == "":
            self.prompt = self._prompt
        response = self.chat_completion.create(
            model=model,
            messages=[
                {"role": "system", "content": self.prompt},
                {"role": "user", "content": f"{review} NAME={name_client} GRADE={grade}"}
            ]

        )
        if response.choices[0].message.content == "":
            return ""
        else:
            response_gpt = response.choices[0].message.content
        if return_amount_tokens is True:
            self.tokens += len(self._encoding.encode(response_gpt))
        return response_gpt
