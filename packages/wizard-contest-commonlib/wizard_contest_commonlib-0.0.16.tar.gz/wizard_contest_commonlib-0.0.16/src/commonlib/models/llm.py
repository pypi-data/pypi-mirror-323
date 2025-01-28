import typing as tp
from typing import TypedDict

from pydantic import BaseModel


class Message(TypedDict):
    content: str
    role: tp.Literal['system', 'user', 'assistant']


class GenerateActionResponse(BaseModel):
    new_actions: list[Message]
    description: str
