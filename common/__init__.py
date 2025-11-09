from functools import lru_cache

from .types import Session, SessionID
from .config.app import AppSettings, BASE_DIR, KNOWLEDGE_BASE_DIR, AVATARS_DIR
from logger import create_logger


@lru_cache
def get_settings() -> AppSettings:
    return AppSettings()


logger = create_logger('mirror')

__all__ = [
    'logger',
    'AppSettings',
    'BASE_DIR',
    'KNOWLEDGE_BASE_DIR',
    'AVATARS_DIR',
    'Session',
    'SessionID',
]
