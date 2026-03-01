from abc import ABC, abstractmethod
from uuid import uuid4

from langchain_core.runnables.config import RunnableConfig
from pydantic import BaseModel

from pounce.model.base import BaseLLMModel


class BaseAgent(ABC):
    def __init__(self, model: BaseLLMModel):
        self._model = model
        self._token = {'input_tokens': 0, 'output_tokens': 0}
        self._id = uuid4().hex

    @property
    def model(self) -> BaseLLMModel:
        return self._model

    @property
    def agent_id(self) -> str:
        return self._id

    @property
    def used_token(self) -> dict:
        return self._token

    @abstractmethod
    async def get_graph(self):
        ...

    async def ainvoke(self, input: BaseModel, recursion_limit=30, **kwargs):
        graph = await self.get_graph()
        result = await graph.ainvoke(
            input=input,
            config=RunnableConfig(recursion_limit=recursion_limit),
            **kwargs
        )
        return result
