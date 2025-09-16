"""Generation modules for LLM and text generation."""

from .generator import DummyLLM, Generator
from .openrouter_client import chat_with_openrouter
from .prompting import build_json_prompt

__all__ = ["DummyLLM", "Generator", "chat_with_openrouter", "build_json_prompt"]
