from langchain_core.language_models import LanguageModelInput
from langchain_core.messages import BaseMessage
from langchain_core.runnables import ConfigurableField, Runnable
from langchain_core.runnables.utils import AnyConfigurableField

from langchain_openai import ChatOpenAI

from common import logger, AppSettings
from common.enums import LLMProvider

_llm_model = None


def get_llm(settings: AppSettings) -> Runnable[LanguageModelInput, BaseMessage]:
    global _llm_model

    if _llm_model is not None:
        return _llm_model

    logger.debug('Initializing LLM model')
    sts = settings.llm

    params = sts.get_config(sts.PROVIDER)
    logger.info(f'Initializing LLM model with provider: {sts.PROVIDER} Config: {sts}')
    _llm_model = ChatOpenAI(**params)

    return _llm_model
