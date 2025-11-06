from .supabase import supabase
from .telegram import create_client, TelegramClient

from common import get_settings

settings = get_settings()

_telegram_client = None


def create_telegram_client() -> TelegramClient:
    global _telegram_client

    if _telegram_client is not None:
        return _telegram_client

    _telegram_client = create_client(
        token=settings.TELEGRAM_TOKEN.get_secret_value(),
        chat_id=settings.TELEGRAM_CHAT_ID,
    )

    return _telegram_client


__all__ = [
    'supabase',
    'create_telegram_client',
    'TelegramClient',
]
