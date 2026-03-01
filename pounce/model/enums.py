from enum import Enum

class ModelEnum(Enum):
    qwen3_vl_235b_a22b_instruct = ('qwen3-vl-235b-a22b-instruct', 'openai', 'qwen')
    gemini_25_pro = ('gemini-2.5-pro', 'google_genai', 'gemini')

    def __init__(self, model_name, provider, model_module):
        self.model_name = model_name
        self.provider = provider
        self.model_module = model_module