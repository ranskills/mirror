import os
from pathlib import Path
from typing import Annotated

from pydantic import SecretStr, Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from .llm import LLMSettings


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    SUPABASE_URL: Annotated[str, Field(...)]
    SUPABASE_KEY: Annotated[SecretStr, Field(...)]

    TELEGRAM_TOKEN: Annotated[SecretStr, Field(...)]
    TELEGRAM_CHAT_ID: Annotated[str, Field(...)]

    llm: Annotated[LLMSettings, Field(default_factory=lambda: LLMSettings())]


BASE_DIR = Path(os.environ.get('BASE_DIR', Path(__file__).parent.parent.parent))

KNOWLEDGE_BASE_DIR = BASE_DIR / 'knowledge-base'
AVATARS_DIR = BASE_DIR / 'avatars'
