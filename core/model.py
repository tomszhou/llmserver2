# -*- coding: utf-8 -*-

from enum import Enum
from typing import Optional,List,Literal

from pydantic import BaseModel


class LlmChat2Role(Enum):
    user = "user"
    assistant = "assistant"
    system = "system"

class LlmChat2Message(BaseModel):
    role : Literal["user", "assistant", "system"]
    content : str

class LlmChatModel(BaseModel):
    messages : List[LlmChat2Message]
    stream : Optional[bool] = False


class LlmChat2Model(BaseModel):
    model : str
    messages : List[LlmChat2Message]
    stream : Optional[bool] = False
    temperature : float
    top_p : float
    top_k : float
    with_search_enhance : Optional[bool] = False
