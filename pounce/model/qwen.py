import os
from typing import List, Tuple

from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel

from pounce.model import ModelEnum
from pounce.model.base import BaseLLMModel
from pounce.utils.coordinate_util import CoordinateUtil


class QwenModel(BaseLLMModel):

    def __init__(self, model: ModelEnum):
        super().__init__()
        self.model = model

    @property
    def instance(self) -> BaseChatModel:
        if self._instance is None:
            self._instance = init_chat_model(
                self.model.model_name,
                model_provider=self.model.provider,
                api_key=os.environ.get('QWEN_API_KEY'),
                base_url=os.environ.get('QWEN_BASE_URL')
            )
        return self._instance

    def with_structured_output(self, schema, **kwargs):
        return self.instance.with_structured_output(
            schema,
            method="json_mode",
            **kwargs
        )

    def normalization(self, bbox: List[int], screen_width: int, screen_height: int) -> Tuple[List[int], float, float]:
        result = CoordinateUtil.normalization_1000(bbox, screen_width, screen_height)
        return result
