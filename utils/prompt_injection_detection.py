"""
This module provides functions to defend against prompt injection attacks.
"""

import re

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
