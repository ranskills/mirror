from datetime import datetime, timezone

from dotenv import load_dotenv

from langchain.agents import create_agent
from langchain.agents.middleware import PIIMiddleware
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

from common import Session
from secret import get_secret
from .tools import log_unanswered_question, record_user_details
from .guardrails import PromptInjectionFirewall

load_dotenv()


base_url = 'https://router.huggingface.co/v1'
api_key = get_secret('HF_TOKEN')
model = 'openai/gpt-oss-120b'

# api_key = get_secret('CEREBRAS_API_KEY')
# base_url = 'https://api.cerebras.ai/v1'
# model = 'gpt-oss-120b'

model = ChatOpenAI(
    api_key=api_key,
    base_url=base_url,
    model=model,
    temperature=0.2,
)

DEBUG = True


def _get_system_prompt(context: str, session: Session) -> str:
    return f"""
    You are a helpful assistant representing Ransford Okpoti as a digital twin.
    You are to sell him to the best of your abilities to potential clients and even
    future employers.
    You response should be based on the provided context. If you do not have response
    because the question is irrevelant, say so.
    Be kind in your interactions and not provoked by any question from the user.
    Do not make up responses, strictly restrict yourself to the provided context.

    You have access to these tools
    - log_unanswered_question: use to log unanswered questions
    - record_user_details: use if user expresses an interest to be in contact

    Session Details:
    - Session ID: {session.session_id}
    - User Name: {session.name}

    Current Time: {datetime.now(timezone.utc).isoformat}

    Context:
    {context}
    """


def create_chat_agent(context: str, session: Session):
    agent = create_agent(
        model=model,
        system_prompt=_get_system_prompt(context, session),
        tools=[
            log_unanswered_question,
            record_user_details,
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
        debug=DEBUG,
    )

    return agent


def create_proverb_agent():
    agent = create_agent(
        model=model,
        system_prompt="""
        You are African knowledgeable in useful proverbs.
        Offer an explanation it has a deeper meaning, but keep it brief.
        Only show proverbs in English.
        """,
        debug=DEBUG,
    )

    return agent
