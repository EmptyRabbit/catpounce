from pounce.model.base import BaseLLMModel
from pounce.model.enums import ModelEnum
from pounce.model.gemini import GeminiModel
from pounce.model.qwen import QwenModel


class NotSupportModelModule(Exception):
    ...


def get_model(model_type: ModelEnum) -> BaseLLMModel:
    match model_type.model_module:
        case 'qwen':
            return QwenModel(model_type)
        case 'gemini':
            return GeminiModel(model_type)
        case _:
            raise NotSupportModelModule(model_type.model_module)
