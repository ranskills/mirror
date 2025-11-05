from functools import lru_cache

from .types import Session, SessionID
from .config import AppSettings


@lru_cache
def get_settings() -> AppSettings:
    return AppSettings()


__all__ = [
    'AppSettings',
    'Session',
    'SessionID',
]
