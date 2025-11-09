from collections.abc import Generator

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

from common import Session, logger
from .agents import create_chat_agent, create_proverb_agent

load_dotenv()


def chat_llm(
    context: str, message: str, history: list[dict], state: Session
) -> Generator[tuple[str, tuple[str]], None, None]:
    """
    Ask the LLM a question within the context of the session.
    Returns the response and the list of tools used.
    """
    agent = create_chat_agent(context, state)

    try:
        messages = history + [{'role': 'user', 'content': message}]
        stream = agent.stream({'messages': messages}, stream_mode='messages')

        tools = set()
        for token, metadata in stream:
            logger.debug(f'node: {metadata["langgraph_node"]}')
            logger.debug(f'content: {token.content_blocks}')

            if token.content_blocks:
                last_block = token.content_blocks
                print(type(last_block))
                if last_block:
                    block_type = last_block[0]['type']
                    if block_type == 'text' and last_block[0]['text'] != 'null':
                        yield last_block[0]['text'], tools
                    elif block_type == 'tool_call_chunk' and (tool_name := last_block[0]['name']):
                        tools.add(tool_name)

    except Exception as e:
        logger.error(f'Error invoking agent: {e}')
        yield "🔥 I'm sorry, I encountered an error while processing your request.", []


def get_proverb() -> str:
    agent = create_proverb_agent()

    result = agent.invoke(
        {'messages': HumanMessage(content='Give 1 proverb to welcome a new person I am meeting.')}
    )
    return '🌱\n' + result['messages'][-1].content
