import base64
from typing import TypeAlias, Literal

from langchain.agents.middleware import AgentMiddleware, AgentState, hook_config
from langgraph.runtime import Runtime
from langchain_core.messages import AIMessage, HumanMessage

from common import logger
from utils import basic_prompt_injection_detection, advanced_prompt_injection_detection

DefenceStrategy: TypeAlias = Literal['basic', 'advanced']


class PromptInjectionFirewall(AgentMiddleware):
    def __init__(self, strategy: DefenceStrategy = 'basic'):
        super().__init__()


    @hook_config(can_jump_to=['end'])
    def before_agent(self, state: AgentState, runtime: Runtime):
        if not state['messages']:
            return None

        last_message = state['messages'][-1]

        if not isinstance(last_message, HumanMessage):
            return None

        attempt_detected = self._detect_prompt_injection(last_message.content)

        if attempt_detected:
            logger.warning(f'Prompt injection detected. Input: {last_message.content}')

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


    def _detect_prompt_injection(self, prompt: str) -> bool:
        if not prompt:
            return False

        try:
            attempt_detected = advanced_prompt_injection_detection(prompt)
        except Exception as e:
            logger.error(f'Promp injection detection failed, falling back to basic detection. Error: {e}')
            attempt_detected = basic_prompt_injection_detection(prompt)

        return attempt_detected
