from datetime import datetime, timezone

from dotenv import load_dotenv

from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

from secret import get_secret

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


def _get_system_prompt(context: str) -> str:
    return f'''
    You are a helpful assistant representing Ransford Okpoti as a digital twin.
    You are to sell him to the best of your abilities to potential clients and even
    future employers.
    You response should be based on the provided context. If you do not have response
    because the question is irrevelant, say so.
    Be kind in your interactions and not provoked by any question from the user.
    Do not make up responses, strictly restrict yourself to the provided context.

    Current Time: {datetime.now(timezone.utc).isoformat}

    Context:
    {context}
    '''


def create_agent_with_context(context: str):

    agent = create_agent(
        model=model,
        system_prompt=_get_system_prompt(context),
        tools=[
            # live_chat_request_notifier,
            # sent_telegram_message,
            # capture_unanswered_question,
        ],
    )

    return agent
