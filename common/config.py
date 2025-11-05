from typing import Annotated

from pydantic import SecretStr, Field, HttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8', extra='ignore')

    SUPABASE_URL: Annotated[str, Field(...)]
    SUPABASE_KEY: Annotated[SecretStr, Field(...)]
