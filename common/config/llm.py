from typing import Annotated, Any
from pydantic import Field, SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from ..enums import LLMProvider
from .utils import validate_required_fields


LLM_PROVIDER_PREFIXES: dict[LLMProvider, str] = {
    LLMProvider.HUGGINGFACE: 'HF',
    LLMProvider.CEREBRAS: 'CEREBRAS',
    LLMProvider.OLLAMA: 'OLLAMA',
    LLMProvider.OLLAMA_CLOUD: 'OLLAMA_CLOUD',
    LLMProvider.OPENAI: 'OPENAI',
    LLMProvider.GOOGLE: 'GOOGLE',
    LLMProvider.OPENROUTER: 'OPENROUTER',
}


class LLMSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    PROVIDER: Annotated[LLMProvider, Field(default=LLMProvider.OLLAMA, alias='LLM_PROVIDER')]
    VERBOSE: Annotated[bool, Field(default=False, alias='LLM_VERBOSE')]
    DEBUG: Annotated[bool, Field(default=False, alias='LLM_DEBUG')]

    # TEMPERATURE: Annotated[float, Field(default=0.7, ge=0.0, le=2.0)]
    # MAX_TOKENS: Annotated[int, Field(default=1000, ge=1)]

    # Cerebras
    CEREBRAS_API_KEY: Annotated[SecretStr, Field(default='')]
    CEREBRAS_BASE_URL: Annotated[str, Field(default='https://api.cerebras.ai/v1')]
    CEREBRAS_MODEL: Annotated[str, Field(default='gpt-oss-120b')]
    CEREBRAS_TEMPERATURE: Annotated[float, Field(default=0.7, ge=0.0, le=2.0)]
    CEREBRAS_MAX_TOKENS: Annotated[int, Field(default=1000, ge=1)]

    # HuggingFace
    HF_API_KEY: Annotated[SecretStr, Field(default='', alias='HF_TOKEN')]
    HF_BASE_URL: Annotated[str, Field(default='https://router.huggingface.co/v1')]
    HF_MODEL: Annotated[str, Field(default='openai/gpt-oss-120b')]
    HF_TEMPERATURE: Annotated[float, Field(default=0.7, ge=0.0, le=2.0)]
    HF_MAX_TOKENS: Annotated[int, Field(default=1000, ge=1)]

    # Ollama
    OLLAMA_API_KEY: Annotated[SecretStr, Field(default='')]
    OLLAMA_BASE_URL: Annotated[str, Field(default='http://localhost:11434')]
    OLLAMA_MODEL: Annotated[str, Field(default='')]
    OLLAMA_TEMPERATURE: Annotated[float, Field(default=0.7, ge=0.0, le=2.0)]
    OLLAMA_MAX_TOKENS: Annotated[int, Field(default=1000, ge=1)]

    # Ollama Cloud
    OLLAMA_CLOUD_API_KEY: Annotated[SecretStr, Field(default='')]
    OLLAMA_CLOUD_BASE_URL: Annotated[str, Field(default='https://ollama.com/v1')]
    OLLAMA_CLOUD_MODEL: Annotated[str, Field(default='gpt-oss:120b')]
    OLLAMA_CLOUD_TEMPERATURE: Annotated[float, Field(default=0.7, ge=0.0, le=2.0)]
    OLLAMA_CLOUD_MAX_TOKENS: Annotated[int, Field(default=1000, ge=1)]

    # Google
    GOOGLE_API_KEY: Annotated[SecretStr, Field(default='')]
    GOOGLE_BASE_URL: Annotated[
        str, Field(default='https://generativelanguage.googleapis.com/v1beta/openai/')
    ]
    GOOGLE_MODEL: Annotated[str, Field(default='')]
    GOOGLE_TEMPERATURE: Annotated[float, Field(default=0.7, ge=0.0, le=2.0)]
    GOOGLE_MAX_TOKENS: Annotated[int, Field(default=1000, ge=1)]

    # OpenAI
    OPENAI_API_KEY: Annotated[SecretStr, Field(default='')]
    OPENAI_BASE_URL: Annotated[str, Field(default='https://api.openai.com/v1')]
    OPENAI_MODEL: Annotated[str, Field(default='gpt-4o-mini')]
    OPENAI_TEMPERATURE: Annotated[float, Field(default=0.7, ge=0.0, le=2.0)]
    OPENAI_MAX_TOKENS: Annotated[int, Field(default=1000, ge=1)]

    # OpenRouter
    OPENROUTER_API_KEY: Annotated[SecretStr, Field(default='')]
    OPENROUTER_BASE_URL: Annotated[str, Field(default='https://openrouter.ai/api/v1')]
    # OPENROUTER_MODEL: Annotated[str, Field(default='openai/gpt-oss-20b:free')]
    OPENROUTER_MODEL: Annotated[str, Field(default='meta-llama/llama-3.3-70b-instruct:free')]
    OPENROUTER_TEMPERATURE: Annotated[float, Field(default=0.7, ge=0.0, le=2.0)]
    OPENROUTER_MAX_TOKENS: Annotated[int, Field(default=1000, ge=1)]

    @model_validator(mode='after')
    def validate_provider_config(self):
        if prefix := LLM_PROVIDER_PREFIXES.get(self.PROVIDER):
            return self._validate_provider(prefix)

        return self

    def _validate_provider(self, prefix: str):
        required_fields = {
            f'{prefix}_API_KEY': getattr(self, f'{prefix}_API_KEY').get_secret_value(),
            f'{prefix}_MODEL': getattr(self, f'{prefix}_MODEL'),
            f'{prefix}_TEMPERATURE': getattr(self, f'{prefix}_TEMPERATURE'),
            f'{prefix}_MAX_TOKENS': getattr(self, f'{prefix}_MAX_TOKENS'),
        }
        validate_required_fields(
            required_fields, '{field}' + f" must be set for '{self.PROVIDER}' provider"
        )
        return self

    def get_config(self, provider: LLMProvider) -> dict[str, Any]:
        if prefix := LLM_PROVIDER_PREFIXES.get(provider):
            return {
                'api_key': getattr(self, f'{prefix}_API_KEY').get_secret_value(),
                'base_url': getattr(self, f'{prefix}_BASE_URL'),
                'model': getattr(self, f'{prefix}_MODEL'),
                'temperature': getattr(self, f'{prefix}_TEMPERATURE'),
                'max_tokens': getattr(self, f'{prefix}_MAX_TOKENS'),
            }

        return {}
