from datetime import datetime, timezone

from dotenv import load_dotenv

from langchain.agents import create_agent
from langchain.tools import tool
from langchain_openai import ChatOpenAI

from common import Session
from secret import get_secret
from .tools import log_unanswered_question

load_dotenv()


# base_url='https://router.huggingface.co/v1',
# api_key=get_secret('HF_TOKEN'),
# model='openai/gpt-oss-120b',

api_key = get_secret('CEREBRAS_API_KEY')
base_url = 'https://api.cerebras.ai/v1'
model = 'gpt-oss-120b'

model = ChatOpenAI(
    api_key=api_key,
    base_url=base_url,
    model=model,
    temperature=0.2,
)


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

    Session Details:
    - Session ID: {session.session_id}
    - User Name: {session.name}

    Current Time: {datetime.now(timezone.utc).isoformat}

    Context:
    {context}
    """


def create_agent_with_context(context: str, session: Session):
    agent = create_agent(
        model=model,
        system_prompt=_get_system_prompt(context, session),
        tools=[
            log_unanswered_question,
        ],
        debug=True,
    )

    return agent
