from enum import Enum, auto


class TypeModelChatGpt(Enum):
    GPT4OMINI = "gpt-4o-mini"
    GPT4 = "gpt-4"


class HandlerType(Enum):
    GPTHANDLER = auto()
    TEMPLATEHANDLER = auto()
