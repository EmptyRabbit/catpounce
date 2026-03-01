from abc import ABC, abstractmethod
from typing import Tuple, List

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import BaseMessage


class BaseLLMModel(ABC):

    def __init__(self):
        self._instance: BaseChatModel | None = None

    @property
    @abstractmethod
    def instance(self) -> BaseChatModel:
        ...

    @abstractmethod
    def normalization(self, bbox, screen_width, screen_height) -> Tuple[List[int], int, int]:
        return bbox

    def with_structured_output(self, *args, **kwargs):
        result = self.instance.with_structured_output(*args, **kwargs)
        return result

    async def ainvoke(self, *args, **kwargs) -> BaseMessage:
        result = await self.instance.ainvoke(*args, **kwargs)
        return result
