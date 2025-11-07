from dotenv import load_dotenv

from langchain_core.messages import HumanMessage, ToolMessage

from common import Session

from .agents import create_chat_agent, create_proverb_agent

load_dotenv()


proverb_agent = create_proverb_agent()

def chat_llm(context: str, message: str, history: list[dict], state: Session) -> tuple[str, tuple[str]]:
    """
    Ask the LLM a question within the context of the session.
    Returns the response and the list of tools used.
    """
    agent = create_chat_agent(context, state)

    try:
        messages = history + [{'role': 'user', 'content': message}]
        result = agent.invoke({'messages': messages})

        response_messages = result['messages']
        msgs = response_messages[:-7:-1]
        tools_used = []
        for msg in msgs:
            if isinstance(msg, ToolMessage):
                tools_used.append(msg.name)
            elif isinstance(msg, HumanMessage):
                break

        last_message = response_messages[-1]
        print('Toots Used', tools_used)

        return last_message.content, tuple(tools_used)
    except Exception as e:
        print(f'Error invoking agent: {e}')
        return "🔥 I'm sorry, I encountered an error while processing your request.", []


def get_proverb() -> str:
    result = proverb_agent.invoke({'messages': HumanMessage(content='Give 1 proverb to welcome a new person I am meeting.') })
    return result['messages'][-1].content
