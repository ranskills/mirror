from typing import TypeAlias, Literal

from langchain.agents.middleware import AgentMiddleware, AgentState, hook_config
from langgraph.runtime import Runtime
from langchain_core.messages import AIMessage

from utils import basic_prompt_injection_detection

DefenceStrategy: TypeAlias = Literal['basic', 'advanced']


class PromptInjectionFirewall(AgentMiddleware):
    def __init__(self, strategy: DefenceStrategy = 'basic'):
        super().__init__()

    @hook_config(can_jump_to=['end'])
    def before_agent(self, state: AgentState, runtime: Runtime):
        if not state['messages']:
            return None

        last_message = state['messages'][-1]

        attempt_detected = basic_prompt_injection_detection(last_message.content)

        if attempt_detected:
            print(f'Promp injection detected. Content: {last_message.content}')
            return {
                'messages': [
                    AIMessage(
                        content='🛡️ Play nice, I detected you are trying to perform a prompt injection.'
                    )
                ],
                'jump_to': 'end',
            }

        return None
