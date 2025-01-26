import typing as tp
from typing import TypedDict

from pydantic import BaseModel


class Message(TypedDict):
    content: str
    role: tp.Literal['system', 'user', 'assistant']


class ActionGenerationResponse(BaseModel):
    new_messages: list[Message]
    action: str
