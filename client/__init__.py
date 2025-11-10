from .supabase import supabase
from .telegram import create_client, TelegramClient
from .pushover import create_send_push_notifcation

from common import get_settings, logger

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


send_pushover_notificaiton = create_send_push_notifcation(
    logger=logger,
    token=settings.PUSHOVER_API_KEY.get_secret_value(),
    user=settings.PUSHOVER_USER,
)

__all__ = [
    'supabase',
    'create_telegram_client',
    'send_pushover_notificaiton',
    'TelegramClient',
]
