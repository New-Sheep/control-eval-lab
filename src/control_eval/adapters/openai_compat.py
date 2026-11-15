"""OpenAI-compatible LLM adapter (openai | nvidia | ollama)."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv
from openai import AsyncOpenAI

from control_eval.ports.llm import LlmBundle
from control_eval.settings import ROOT


class OpenAICompatProvider:
    def __init__(self) -> None:
        load_dotenv(ROOT / ".env", override=False)

    def build(
        self, *, provider: str | None = None, model: str | None = None
    ) -> LlmBundle:
        from agents import OpenAIChatCompletionsModel, set_tracing_disabled

        set_tracing_disabled(True)
        raw = (provider or os.environ.get("LLM_PROVIDER") or "openai").strip().lower()

        if raw in ("ollama", "local"):
            base = (
                os.environ.get("OLLAMA_BASE_URL") or "http://127.0.0.1:11434/v1"
            ).rstrip("/")
            model_id = model or os.environ.get("OLLAMA_MODEL") or "qwen2.5:7b-instruct"
            client = AsyncOpenAI(base_url=base, api_key="ollama")
            name = "ollama"
        elif raw in ("nvidia", "nim"):
            key = (os.environ.get("NVIDIA_API_KEY") or "").strip()
            if not key:
                raise RuntimeError(
                    "NVIDIA_API_KEY missing. Set it in .env or use LLM_PROVIDER=openai|ollama."
                )
            base = (
                os.environ.get("NVIDIA_BASE_URL")
                or "https://integrate.api.nvidia.com/v1"
            ).rstrip("/")
            model_id = (
                model or os.environ.get("NVIDIA_MODEL") or "nvidia/nemotron-3.5-bolt-e4b"
            )
            client = AsyncOpenAI(base_url=base, api_key=key)
            name = "nvidia"
        else:
            key = (os.environ.get("OPENAI_API_KEY") or "").strip()
            if not key:
                raise RuntimeError(
                    "OPENAI_API_KEY missing. Set it in .env or use LLM_PROVIDER=ollama|nvidia."
                )
            base = (
                os.environ.get("OPENAI_BASE_URL") or "https://api.openai.com/v1"
            ).rstrip("/")
            model_id = model or os.environ.get("OPENAI_MODEL") or "gpt-4.1-mini"
            client = AsyncOpenAI(base_url=base, api_key=key)
            name = "openai"

        agents_model = OpenAIChatCompletionsModel(model=model_id, openai_client=client)
        return LlmBundle(name=name, model_id=model_id, agents_model=agents_model)
