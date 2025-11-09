from enum import StrEnum


class LLMProvider(StrEnum):
    OLLAMA = 'ollama'
    OLLAMA_CLOUD = 'ollama-cloud'
    OPENAI = 'openai'
    GOOGLE = 'google'
    CEREBRAS = 'cerebras'
    HUGGINGFACE = 'huggingface'
    OPENROUTER = 'openrouter'
