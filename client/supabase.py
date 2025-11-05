from supabase import create_client, Client

from common import get_settings


settings = get_settings()

supabase: Client = create_client(
    supabase_key=settings.SUPABASE_KEY.get_secret_value(),
    supabase_url=settings.SUPABASE_URL,
)
