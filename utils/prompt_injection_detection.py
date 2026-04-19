"""
This module provides functions to defend against prompt injection attacks.
"""

from functools import lru_cache
import re

import torch

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
    from transformers import AutoModelForSequenceClassification, AutoTokenizer, BitsAndBytesConfig


    model_id = 'meta-llama/Llama-Prompt-Guard-2-86M'

    use_4_bit = True

    if use_4_bit:
        quant_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_compute_dtype=torch.bfloat16,
            bnb_4bit_quant_type='nf4',
            bnb_4bit_use_double_quant=True
        )
    else:
        quant_config = BitsAndBytesConfig(
            load_in_8bit=True,
            bnb_8bit_compute_dtype=torch.bfloat16,
        )

    tokenizer = AutoTokenizer.from_pretrained(model_id)
    model = AutoModelForSequenceClassification.from_pretrained(
        model_id,
        quantization_config=quant_config,
        device_map="auto" # Dynamically places model on CPU/GPU
    )

    # No significan't change in memory usaged. 4bit = 815.91 MB.  8bit = 858.67 MB. None = 1115.25 MB
    logger.info(f'Model loaded! Memory used: {model.get_memory_footprint() / 1e6:.2f} MB')

    return tokenizer, model


def advanced_prompt_injection_detection(text: str) -> bool:
    """
    Advanced detection using a pre-trained model to detect prompt injection and jailbreak attempts.
    """
    tokenizer, model = _get_prompt_guard_model()

    inputs = tokenizer(text, return_tensors='pt').to(model.device)

    with torch.no_grad():
        logits = model(**inputs).logits

    predicted_class_id = logits.argmax().item()
    label = model.config.id2label[predicted_class_id]

    probabilities = torch.softmax(logits, dim=-1)
    confidence = probabilities[0][predicted_class_id].item()

    logger.debug(f'{label}. {confidence}')
    is_malicious = label == 'LABEL_1'

    return is_malicious and confidence >= 0.85
