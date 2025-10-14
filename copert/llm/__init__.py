"""LLM integration module."""

from copert.llm.client import CopertLLM, create_llm
from copert.llm.prompts import (
    COPERT_SYSTEM_PROMPT,
    GENERAL_PURPOSE_SUBAGENT_PROMPT,
    CODE_WRITER_SUBAGENT_PROMPT,
)

__all__ = [
    "CopertLLM",
    "create_llm",
    "COPERT_SYSTEM_PROMPT",
    "GENERAL_PURPOSE_SUBAGENT_PROMPT",
    "CODE_WRITER_SUBAGENT_PROMPT",
]
