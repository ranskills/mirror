from functools import lru_cache

from .types import Session, SessionID
from .config import AppSettings, BASE_DIR, KNOWLEDGE_BASE_DIR, AVATARS_DIR


@lru_cache
def get_settings() -> AppSettings:
    return AppSettings()


__all__ = [
    'AppSettings',
    'BASE_DIR',
    'KNOWLEDGE_BASE_DIR',
    'AVATARS_DIR',
    'Session',
    'SessionID',
]
