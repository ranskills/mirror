from datetime import datetime, timezone

from dotenv import load_dotenv

from langchain.agents import create_agent
from langchain.agents.middleware import PIIMiddleware

from common import Session, BASE_DIR, get_settings
from .tools import log_unanswered_question, record_user_details, send_push_notification
from .guardrails import PromptInjectionFirewall
from .model import get_llm
from .promptloader import PromptLoader


load_dotenv()


settings = get_settings()
model = get_llm(settings)

promptloader = PromptLoader(BASE_DIR / 'llm/prompts')

PROVERB_SYSTEM_PROMPT = promptloader.load('proverb')
CHAT_SYSTEM_PROMPT = promptloader.load('chat', 'v1.0')


def _get_system_prompt(context: str, session: Session) -> str:
    return CHAT_SYSTEM_PROMPT.format(
        context=context,
        session=session,
        current_time=datetime.now(timezone.utc).isoformat,
    )


def create_chat_agent(context: str, session: Session):
    agent = create_agent(
        model=model,
        system_prompt=_get_system_prompt(context, session),
        tools=[
            log_unanswered_question,
            record_user_details,
            send_push_notification,
        ],
        middleware=[
            PromptInjectionFirewall(strategy='basic'),
            PIIMiddleware('email', strategy='redact', apply_to_output=True),
            PIIMiddleware(
                'phone_number',
                detector=r'(\+\d{1,3}\s?)?(\(?\d+\)?[-\s]?){2,}\d+',
                strategy='mask',
                apply_to_output=True,
            ),
        ],
        debug=settings.llm.DEBUG,
    )

    return agent


def create_proverb_agent():
    agent = create_agent(
        model=model,
        system_prompt=PROVERB_SYSTEM_PROMPT,
        debug=settings.llm.DEBUG,
    )

    return agent
