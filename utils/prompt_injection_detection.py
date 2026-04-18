"""
This module provides functions to defend against prompt injection attacks.
"""

from functools import lru_cache
import re

from common import logger


action_regex = None
system_regex = None


def basic_prompt_injection_detection(text: str) -> bool:
    global action_regex, system_regex

    text = text.replace('.', '').replace('-', '')

    system_reference_terms = [
        'prompt',
        'command',
        'instruction',
        'programming',
        'guideline',
        'rules',
        'regulation',
        'policies',
        'policy',
        'procedure',
        'protocol',
        'directive',
        'system',
        'initial',
        # 2025-10-07
        'task',
        'objective',
        'goal',
        'mission',
        'function',
        'responsibility',
        'duty',
        'role',
        'assignment',
    ]

    # Actions used to manipulate/override the system
    action_terms = [
        'forget',
        'ignore',
        'delete',
        'remove',
        'erase',
        'discard',
        'clear',
        'reset',
        'disregard',
        'dismiss',
        'overlook',
        'shun',
        'substitute',
        'lose',
        'bypass',
        'override',
        'stop',
        'pretend',
        'act',
        # 2025-10-07
        'replace',
        'change',
        'modify',
        'alter',
        'revise',
        'redefine',
        'reformulate',
        'rephrase',
        'abandon',
        'switch',
        'suppress',
        'focus',
    ]

    if action_regex is None:
        action_regex = re.compile(r'|'.join(action_terms), re.IGNORECASE)
    if system_regex is None:
        system_regex = re.compile(r'|'.join(system_reference_terms), re.IGNORECASE)

    has_system_reference = bool(system_regex.search(text))
    has_manipulation_action = bool(action_regex.search(text))

    return has_system_reference and has_manipulation_action


@lru_cache(maxsize=1)
def _get_prompt_guard_model():
    from transformers import pipeline

    classifier = pipeline('text-classification', model='meta-llama/Llama-Prompt-Guard-2-86M')
    return classifier


def advanced_prompt_injection_detection(text: str) -> bool:
    """
    Advanced detection using a pre-trained model to detect prompt injection and jailbreak attempts.
    """
    classifier = _get_prompt_guard_model()
    result = classifier(text)
    result = result[0]

    logger.debug(f'Prompt Injection Detection. Input: {text}  Result: {result}')

    is_malicious = result['label'] == 'LABEL_1'

    return is_malicious and result['score'] >= 0.8
